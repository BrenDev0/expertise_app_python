# core/decorators/error_handling.py
from functools import wraps
import logging
from typing import Callable, Any


def service_error_handler(module: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func) 
        def wrapper(self, *args: Any, **kwargs: Any) -> Any:
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self._logger.log(
                    message=f"Error in {func.__name__}",
                    level=logging.ERROR,
                    name=f"{module}.{func.__name__}",
                    exc_info=True
                )
                raise  
        return wrapper
    return decorator