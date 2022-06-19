from utils.logger import Logger


logger = Logger()

def log_exceptions(func):
    def wrapper(self, *args, **kargs):
        try:
            return func(self, *args, **kargs)
        except Exception as e:
            logger.error(f"error in '{func.__name__}' function: {e}")
    return wrapper