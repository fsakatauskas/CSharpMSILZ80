"""Interface for code generator service."""
from abc import ABC, abstractmethod
from typing import Any


class ICodeGenerator(ABC):
    """Protocol for generating LR35902 machine code from IR."""
    
    @abstractmethod
    def generate(self, ir_module: Any) -> bytes:
        """
        Generate LR35902 machine code from intermediate representation.
        
        Args:
            ir_module: Intermediate representation module
            
        Returns:
            Raw machine code bytes
        """
        pass

