"""Interface for IR builder service."""
from abc import ABC, abstractmethod
from typing import Any


class IIrBuilder(ABC):
    """Protocol for building intermediate representation from assembly."""
    
    @abstractmethod
    def build(self, assembly: Any) -> Any:
        """
        Build intermediate representation from parsed assembly.
        
        Args:
            assembly: Parsed .NET assembly
            
        Returns:
            IR module containing methods, types, etc.
        """
        pass

