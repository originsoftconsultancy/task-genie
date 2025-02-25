import sqlite3
from typing import List, Tuple, Any
from dotenv import load_dotenv
import os

load_dotenv()


def create_table(table_name: str, columns: str):
    """Create a table with the given name and columns."""
    conn = sqlite3.connect(os.getenv('STORAGE_DB'))
    cursor = conn.cursor()

    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns})')

    conn.commit()
    conn.close()


def insert_data(table_name: str, columns: str, values: Tuple[Any, ...]):
    """Insert data into the specified table."""
    conn = sqlite3.connect(os.getenv('STORAGE_DB'))
    cursor = conn.cursor()

    placeholders = ', '.join(['?' for _ in values])
    cursor.execute(
        f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', values)

    conn.commit()
    conn.close()


def fetch_data(table_name: str, columns: str = '*', where_clause: str = '', where_values: Tuple[Any, ...] = ()):
    """Fetch data from the specified table."""
    conn = sqlite3.connect(os.getenv('STORAGE_DB'))
    cursor = conn.cursor()

    query = f'SELECT {columns} FROM {table_name}'
    if where_clause:
        query += f' WHERE {where_clause}'

    cursor.execute(query, where_values)
    rows = cursor.fetchall()

    conn.close()
    return rows


def update_data(table_name: str, set_clause: str, where_clause: str, values: Tuple[Any, ...]):
    """Update data in the specified table."""
    conn = sqlite3.connect(os.getenv('STORAGE_DB'))
    cursor = conn.cursor()

    query = f'UPDATE {table_name} SET {set_clause} WHERE {where_clause}'
    cursor.execute(query, values)

    conn.commit()
    conn.close()


def delete_data(table_name: str, where_clause: str, where_values: Tuple[Any, ...]):
    """Delete data from the specified table."""
    conn = sqlite3.connect(os.getenv('STORAGE_DB'))
    cursor = conn.cursor()

    query = f'DELETE FROM {table_name} WHERE {where_clause}'
    cursor.execute(query, where_values)

    conn.commit()
    conn.close()
