# -*- coding:utf-8 -*-

def empty_function(*args, **kwargs):
    pass

def exists_in(seq, element):
    for e in seq:
        if e == element:
            return True
    return False

def uniquify(seq):
    seen = set()
    result = []
    for item in seq:
        if item in seen: continue
        seen.add(item)
        result.append(item)
    return result

class Singleton(object):
    @classmethod
    def instance(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = cls(*args, **kwargs)
        return cls._inst
