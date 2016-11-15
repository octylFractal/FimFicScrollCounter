from __future__ import print_function
from util import py3


def fix(builtin):
    isdict = type(builtin) is dict

    def moduleset(k, v):
        setattr(builtin, k, v)

    def moduleget(k, d=None):
        return getattr(builtin, k, d)

    # default to module
    set_ = moduleset
    get_ = moduleget
    dbins = dir(builtin)

    if isdict:
        # dict of builtins, use it
        dbins = builtin

        def dictset(k, v):
            builtin[k] = v

        def dictget(k, d=None):
            return builtin.get(k, d)

        set_ = dictset
        get_ = dictget

    def has(s):
        return s in dbins

    def mv(here, there):
        set_(there, get_(here))

    if has("xrange"):
        mv("xrange", "range")
    if has("raw_input"):
        mv("raw_input", "input")


if py3:
    fix(__import__('builtins'))
else:
    fix(__import__('__builtin__'))
__all__ = []
