from distutils.core import setup
from setuptools import find_packages
from os.path import join, dirname, basename, isdir
from glob import glob

def locate_locales():
    result = []
    for langdir in glob('share/locale/*'):
        if not isdir(langdir):
            continue
        result.append((langdir+'/LC_MESSAGES', glob(langdir+'/LC_MESSAGES/*.mo')))
    print result
    return result


setup(
    name = 'palette-editor',
    version = '0.0.5',
    author = 'Ilya Portnov',
    author_email = 'portnov84@rambler.ru',
    scripts = ['bin/gui.py', 'bin/cluster.py', 'bin/palette_viewer.py'],
    url = 'https://github.com/portnov/color-palette',
    license = 'LICENSE',
    description = 'Set of Python (+Qt) scripts to work with colors, color harmonies, mixing of colors, and edit color palettes',
    long_description = open(join(dirname(__file__), 'README')).read(),
    include_package_data = True,
    packages = find_packages(),
    install_requires = [
        "numpy >= 1.8.1",
        "lxml >= 2.3.2",
        "appdirs >= 1.2.0"
    ],
    data_files = [
                    ('share/palette-editor/icons', glob('share/icons/*.png')),
                    ('share/palette-editor/palettes', glob('share/palettes/*')),
                    ('share/palette-editor/templates', glob('share/templates/*.svg')),
                ] + locate_locales()
)

