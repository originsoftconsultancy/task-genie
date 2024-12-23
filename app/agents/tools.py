from pydantic_ai import Tool


def greet_tool(query: str) -> str:
    return f"Hello! You said: {query}"


greet = Tool(
    name="Greet", description="Responds with a greeting.", function=greet_tool)


# Export tools as a list
TOOLS = [greet]
