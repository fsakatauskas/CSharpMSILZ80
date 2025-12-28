"""Interface for MSIL reader service."""
from abc import ABC, abstractmethod
from typing import Any


class IMsilReader(ABC):
    """Protocol for reading and parsing .NET assemblies."""
    
    @abstractmethod
    def read_assembly(self, path: str) -> Any:
        """
        Read and parse a .NET assembly file.
        
        Args:
            path: Path to the .NET assembly (.dll) file
            
        Returns:
            Parsed assembly object containing type definitions, methods, etc.
        """
        pass

