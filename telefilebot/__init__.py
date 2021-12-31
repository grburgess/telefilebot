# -*- coding: utf-8 -*-

"""Top-level package for telefilebot."""

__author__ = """J. Michael Burgess"""
__email__ = 'jburgess@mpe.mpg.de'

from .bot import TeleFileBot
from .utils.read_input_file import read_input_file




from . import _version
__version__ = _version.get_versions()['version']
