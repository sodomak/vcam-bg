from enum import Enum, auto
from typing import Dict
from importlib import import_module

class Language(Enum):
    """Supported languages"""
    ENGLISH = auto()
    CZECH = auto()

class Strings:
    """Manages localized strings"""
    def __init__(self, language: Language = Language.ENGLISH):
        self.language = language
        self._strings = self._load_strings()

    def _load_strings(self) -> Dict[str, str]:
        """Load strings for current language"""
        module_name = {
            Language.ENGLISH: 'locales.en.strings',
            Language.CZECH: 'locales.cs.strings'
        }[self.language]
        
        return import_module(module_name).STRINGS

    def get(self, key: str) -> str:
        """Get localized string by key"""
        return self._strings.get(key, f"Missing string: {key}")

    def change_language(self, language: Language):
        """Change current language"""
        self.language = language
        self._strings = self._load_strings()
