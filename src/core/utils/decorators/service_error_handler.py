# core/decorators/error_handling.py
from functools import wraps
from typing import Callable, Any
import logging


def service_error_handler(module: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func) 
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = logging.getLogger(module)
                logger.error(e)
                raise  
        return wrapper
    return decorator