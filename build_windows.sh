#!/bin/bash

set -e

wine C:/Python27/python.exe C:/PyInstaller-3.2/pyinstaller.py palette_editor.spec
makensis colors.nsis
