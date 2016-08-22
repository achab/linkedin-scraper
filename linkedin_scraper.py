#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

print(sys.version)

def reexec_with_pythonw(file = None):
    if sys.platform == 'darwin' and not sys.executable.endswith('MacOS/Python'):
        print >> sys.stderr, 're-executing using pythonw'
        if file:
            os.execvp('pythonw', ['pythonw', file] + sys.argv[1:])
        else:
            os.execvp('pythonw', ['pythonw', __file__] + sys.argv[1:])

if __name__ == '__main__':
    filename = "main.py"
    reexec_with_pythonw(filename)
