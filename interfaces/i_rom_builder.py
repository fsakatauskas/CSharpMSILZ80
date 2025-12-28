"""Interface for ROM builder service."""
from abc import ABC, abstractmethod
from typing import Dict, Any


class IRomBuilder(ABC):
    """Protocol for building valid Game Boy ROM files."""
    
    @abstractmethod
    def build(self, code: bytes, config: Dict[str, Any]) -> bytes:
        """
        Build a valid .gb ROM file with header and checksums.
        
        Args:
            code: Generated machine code
            config: ROM configuration (title, cartridge type, etc.)
            
        Returns:
            Complete ROM file bytes
        """
        pass

