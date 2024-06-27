import time
import hashlib
import functools
import streamlit as st

# Decorator for logging function calls
def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        st.write(f"Calling {func.__name__} function...")
        return func(*args, **kwargs)
    return wrapper

# Decorator for timing function execution
def time_function_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        st.write(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper

# Decorator for caching function results
def cache_results(func):
    cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = func.__name__ + hashlib.md5(str(args).encode('utf-8')).hexdigest()
        if key in cache:
            st.write(f"Returning cached result for {func.__name__} function...")
            return cache[key]
        else:
            result = func(*args, **kwargs)
            cache[key] = result
            return result
    return wrapper
