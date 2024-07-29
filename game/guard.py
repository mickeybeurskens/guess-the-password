import json
from abc import ABC, abstractmethod
from enum import Enum

import requests
from pydantic import BaseModel, Field


class Guard(ABC):
    def __init__(self, password: str):
        self.password = password

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return one-time startup system prompt for this level."""

    @abstractmethod
    def get_repeated_prompt(self) -> str:
        """Return a prompt that is injected at every user query"""

    @abstractmethod
    def check_query(self, query: str) -> tuple[bool, str]:
        """Checks the input query and returns true if ok and response on false."""

    @abstractmethod
    def check_response(self, query: str) -> tuple[bool, str]:
        """Checks the model response and returns true if ok and response on false."""

    @abstractmethod
    def hint(self) -> str:
        """Message displayed as a hint."""

    @abstractmethod
    def name(self) -> str:
        """Name for the guard level."""
