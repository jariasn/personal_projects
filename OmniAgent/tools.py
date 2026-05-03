# tools.py
from abc import ABC, abstractmethod
import os

# Base Tool class
class Tool(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass

# TextFileCreationTool class
class TextFileCreationTool(Tool):
    def __init__(self):
        self.name = "CreateTextFile"

    def execute(self, filename: str, content: str) -> str:
        # Create the text file with the given content
        with open(filename, 'w') as file:
            file.write(content)
        return f"File '{filename}' created successfully."

    def description(self) -> str:
        return "Creates a text file with the specified filename and content."