"""
cache_manager.py
-----------------
Demonstrates BOTH caching strategies required by the assignment.

set_llm_cache(...) registers one global cache; every LLM call checks it
first — an identical prompt + model + params combination is served from
cache instead of triggering a new (paid) API call.

InMemoryCache -> RAM only. Fastest. Wiped on restart. Good for fast repeated
                 tests within one session.
SQLiteCache   -> a `.db` file on disk. Slightly slower than RAM but survives
                 app restarts, so repeat questions stay free/instant across
                 days, not just within one run.
"""

from langchain_core.globals import set_llm_cache
from langchain_community.cache import InMemoryCache, SQLiteCache

CACHE_DB_PATH = ".langchain_cache.db"

_current_cache_mode = "none"


def enable_in_memory_cache():
    global _current_cache_mode
    set_llm_cache(InMemoryCache())
    _current_cache_mode = "in_memory"


def enable_sqlite_cache(db_path: str = CACHE_DB_PATH):
    global _current_cache_mode
    set_llm_cache(SQLiteCache(database_path=db_path))
    _current_cache_mode = "sqlite"


def disable_cache():
    global _current_cache_mode
    set_llm_cache(None)
    _current_cache_mode = "none"


def get_cache_mode() -> str:
    return _current_cache_mode


def apply_cache_choice(choice: str):
    """Helper used directly by app.py's sidebar selectbox.

    choice: one of "None", "In-Memory", "SQLite"
    """
    if choice == "In-Memory":
        enable_in_memory_cache()
    elif choice == "SQLite":
        enable_sqlite_cache()
    else:
        disable_cache()
