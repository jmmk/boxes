from setuptools import setup, find_packages

setup(
    name = 'boxes',
    version = '0.1.0',
    description = 'Grid-based window manipulation for Linux',
    author = 'Michael McLellan',
    url = 'https://github.com/jmmk/boxes',
    license = 'MIT',

    packages = find_packages(),
    keywords = 'window manager resize grid divvy shiftit slate xmonad',
)
