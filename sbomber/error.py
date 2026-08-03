class SbomberError(Exception):
    pass

def raise_error_if(condition: bool, msg):
    if condition:
        raise SbomberError(msg)
