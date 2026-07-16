import functools
from utils.logger import get_logger

logger = get_logger("decorators")

def log_action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # args[0] is typically self/cls, so we log args[1:]
        logged_args = args[1:] if len(args) > 0 else args
        logger.info(f"Action start: {func.__name__} | args={logged_args} | kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Action success: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Action error in {func.__name__}: {str(e)}", exc_info=True)
            raise e
    return wrapper
