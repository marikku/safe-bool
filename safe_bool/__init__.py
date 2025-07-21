# safe_bool/__init__.py

from distutils.util import strtobool as _strtobool

def safe_strtobool(val):
    if isinstance(val, bool): return val
    if isinstance(val, (int, float)): return val != 0
    if isinstance(val, str):
        try: return bool(_strtobool(val.strip().lower()))
        except: return False
    return False
