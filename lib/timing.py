import time
from functools import wraps

def function_timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        time_start = time.time()
        result = func(*args, **kwargs)
        time_end = time.time()
        print('Function call took {}s'.format(time_end - time_start))
        return result
    return wrapper
