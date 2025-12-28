"""Interface for type resolver service."""
from abc import ABC, abstractmethod
from typing import Any, Dict


class ITypeResolver(ABC):
    """Protocol for mapping C# types to Game Boy memory layouts."""
    
    @abstractmethod
    def resolve_type(self, csharp_type: Any) -> Dict[str, Any]:
        """
        Resolve a C# type to its Game Boy memory layout.
        
        Args:
            csharp_type: C# type from assembly
            
        Returns:
            Dictionary with size, alignment, and layout information
        """
        pass
    
    @abstractmethod
    def get_type_size(self, csharp_type: Any) -> int:
        """
        Get the size in bytes of a C# type on Game Boy.
        
        Args:
            csharp_type: C# type from assembly
            
        Returns:
            Size in bytes
        """
        pass

