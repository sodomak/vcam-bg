import os
import importlib

def get_strings(lang='en'):
    """Get strings for the specified language"""
    try:
        strings = importlib.import_module(f'src.locales.{lang}.strings')
        return strings
    except ImportError:
        # Fallback to English if requested language is not available
        strings = importlib.import_module('src.locales.en.strings')
        return strings 