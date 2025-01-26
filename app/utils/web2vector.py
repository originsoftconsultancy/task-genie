from dataclasses import dataclass
import datetime
from datetime import timezone
import json
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from typing import Any, List, Dict
import os
import sys
import numpy as np
import psutil
import asyncio
from pydantic_ai import Agent
import requests
from xml.etree import ElementTree
from FlagEmbedding import FlagModel
from pydantic_ai.models.ollama import OllamaModel
from supabase import create_client, Client

__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "output")

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)


@dataclass
class ProcessedChunk:
    url: str
    chunk_number: int
    title: str
    summary: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]


title_summary_extractor = None


def get_all_docs_urls(sitemap_url):
    f"""
    Fetches all URLs from the given sitemap url.
    Uses the sitemap ({sitemap_url}) to get these URLs.

    Returns:
        List[str]: List of URLs
    """

    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        # Parse the XML
        root = ElementTree.fromstring(response.content)

        # Extract all URLs from the sitemap
        # The namespace is usually defined in the root element
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]

        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []


async def crawl_parallel(urls: List[str], max_concurrent: int = 5):
    """Crawl multiple URLs in parallel with a concurrency limit."""
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu",
                    "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_url(url: str):
            async with semaphore:
                result = await crawler.arun(
                    url=url,
                    config=crawl_config,
                    session_id="session1"
                )
                if result.success:
                    print(f"Successfully crawled: {url}")
                    await process_and_store_document(url, result.markdown_v2.raw_markdown)
                else:
                    print(f"Failed: {url} - Error: {result.error_message}")

        # Process all URLs in parallel with limited concurrency

        await asyncio.gather(*[process_url(url) for url in urls])
    finally:
        await crawler.close()


def chunk_text(text: str, chunk_size: int = 5000) -> List[str]:
    """Split text into chunks, respecting code blocks and paragraphs."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # Calculate end position
        end = start + chunk_size

        # If we're at the end of the text, just take what's left
        if end >= text_length:
            chunks.append(text[start:].strip())
            break

        # Try to find a code block boundary first (```)
        chunk = text[start:end]
        code_block = chunk.rfind('```')
        if code_block != -1 and code_block > chunk_size * 0.3:
            end = start + code_block

        # If no code block, try to break at a paragraph
        elif '\n\n' in chunk:
            # Find the last paragraph break
            last_break = chunk.rfind('\n\n')
            if last_break > chunk_size * 0.3:  # Only break if we're past 30% of chunk_size
                end = start + last_break

        # If no paragraph break, try to break at a sentence
        elif '. ' in chunk:
            # Find the last sentence break
            last_period = chunk.rfind('. ')
            if last_period > chunk_size * 0.3:  # Only break if we're past 30% of chunk_size
                end = start + last_period + 1

        # Extract chunk and clean it up
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position for next chunk
        start = max(start + 1, end)

    return chunks


async def get_title_and_summary(chunk: str, url: str) -> Dict[str, str]:
    """Extract title and summary using Ollama."""

    global title_summary_extractor

    system_prompt = """You are an AI agent that extracts titles and summaries from documentation chunks.
    Return a JSON object with 'title' and 'summary' keys.
    For the title: If this seems like the start of a document, extract its title. If it's a middle chunk, derive a descriptive title.
    For the summary: Create a concise summary of the main points in this chunk.
    Keep both title and summary concise but informative."""

    try:
        if not title_summary_extractor:
            title_summary_extractor = Agent(
                OllamaModel(os.getenv("LLM_MODEL")),
                name="assistant",
                deps_type=str,
                result_type=Dict[str, str],
                system_prompt=system_prompt,
                tools=[]
            )

        response = await title_summary_extractor.run(f"URL: {url}\n\nContent:\n{chunk[:1000]}...")
        return response.data
    except Exception as e:
        print(f"Error getting title and summary: {e}")
        return {"title": "Error processing title", "summary": "Error processing summary"}


async def get_embedding(text: str) -> List[float]:
    """Get embedding vector from OpenAI."""
    try:
        model = FlagModel('BAAI/bge-base-en-v1.5',
                          query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
                          use_fp16=True)
        return model.encode(text).tolist()
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 768  # Return zero vector on error


async def process_chunk(chunk: str, chunk_number: int, url: str) -> ProcessedChunk:
    """Process a single chunk of text."""
    # Get title and summary
    extracted = await get_title_and_summary(chunk, url)

    # Get embedding
    embedding = await get_embedding(chunk)

    # Create metadata
    metadata = {
        "source": "pydantic_ai_docs",
        "chunk_size": len(chunk),
        "crawled_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "url_path": urlparse(url).path
    }

    return ProcessedChunk(
        url=url,
        chunk_number=chunk_number,
        title=extracted['title'],
        summary=extracted['summary'],
        content=chunk,  # Store the original chunk content
        metadata=metadata,
        embedding=embedding
    )


async def insert_chunk(chunk: ProcessedChunk):
    """Insert a processed chunk into Supabase."""
    try:
        data = {
            "url": chunk.url,
            "chunk_number": chunk.chunk_number,
            "title": chunk.title,
            "summary": chunk.summary,
            "content": chunk.content,
            "metadata": chunk.metadata,
            "embedding": chunk.embedding
        }

        result = supabase.table("site_pages").insert(data).execute()
        print(f"Inserted chunk {chunk.chunk_number} for {chunk.url}")
        return result
    except Exception as e:
        print(f"Error inserting chunk: {e}")
        return None


async def process_and_store_document(url: str, markdown: str):
    """Process a document and store its chunks in parallel."""
    # Split into chunks
    chunks = chunk_text(markdown)

    # Process chunks in parallel
    tasks = [
        process_chunk(chunk, i, url)
        for i, chunk in enumerate(chunks)
    ]
    processed_chunks = await asyncio.gather(*tasks)

    # Store chunks in parallel
    insert_tasks = [
        insert_chunk(chunk)
        for chunk in processed_chunks
    ]
    await asyncio.gather(*insert_tasks)


async def main():
    sitemap = "https://ai.pydantic.dev/sitemap.xml"
    urls = get_all_docs_urls(sitemap)
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel(urls, max_concurrent=1)
    else:
        print("No URLs found to crawl")

if __name__ == "__main__":
    asyncio.run(main())
