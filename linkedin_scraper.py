#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

def reexec_with_pythonw(file = None):
    if sys.platform == 'darwin' and not sys.executable.endswith('MacOS/Python'):
        print >> sys.stderr, 're-executing using pythonw'
        if file:
            print("first option")
            os.execvp('pythonw', ['pythonw', file] + sys.argv[1:])
        else:
            print("second option")
            os.execvp('pythonw', ['pythonw', __file__] + sys.argv[1:])

import gui_app
#dir_path = os.path.dirname(os.path.realpath(filename))
#filename = os.path.join(dir_path, "main.py")
#filename = dir_path + "/" + filename
#filename = os.path.abspath("main.py")
reexec_with_pythonw(gui_app.__file__)
