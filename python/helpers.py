
def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

class PanicModeException(Exception):
    pass