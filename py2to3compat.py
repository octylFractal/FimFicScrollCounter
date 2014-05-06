from __future__ import print_function
def fix(__builtins__):
    isdict = type(__builtins__) is dict
    # default to module
    delfunction = delattr
    dbins = dir(__builtins__)

    if isdict:
        # dict of builtins, use it
        dbins = __builtins__
        delfunction = dict.pop

    def has(s) :
        return s in dbins
    def rem(s) :
        before = eval(s)
        # delfunction(__builtins__, s)
        return before

    if has("xrange") :
        __builtins__.range = rem("xrange")
    if has("raw_input") :
        __builtins__.input = rem("raw_input")

PYTHON_VERSION_MAJOR = __import__('sys').version_info[0]
