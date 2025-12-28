"""MSIL reader service for parsing .NET assemblies."""
import dnfile
from typing import Any, Optional
from interfaces.i_msil_reader import IMsilReader


class MsilReader(IMsilReader):
    """Reads and parses .NET assemblies using dnfile."""
    
    def read_assembly(self, path: str) -> Any:
        """
        Read and parse a .NET assembly file.
        
        Args:
            path: Path to the .NET assembly (.dll) file
            
        Returns:
            Parsed assembly object (dnfile.pe.PE object)
        """
        try:
            pe = dnfile.dnPE(path)
            return pe
        except Exception as e:
            raise ValueError(f"Failed to read assembly {path}: {e}")
    
    def get_entry_point(self, assembly: Any) -> Optional[Any]:
        """Get the entry point method from assembly."""
        if hasattr(assembly, 'net') and assembly.net:
            if hasattr(assembly.net, 'metadata') and assembly.net.metadata:
                if hasattr(assembly.net.metadata, 'netmetadata'):
                    metadata = assembly.net.metadata.netmetadata
                    if hasattr(metadata, 'entry_point_token'):
                        token = metadata.entry_point_token
                        if token:
                            return assembly.net.metadata.get_entry_point()
        return None
    
    def get_all_types(self, assembly: Any) -> list:
        """Get all types from assembly."""
        types = []
        if hasattr(assembly, 'net') and assembly.net:
            if hasattr(assembly.net, 'metadata'):
                metadata = assembly.net.metadata
                if hasattr(metadata, 'netmetadata'):
                    for row in metadata.netmetadata.tables.TypeDef:
                        types.append(row)
        return types
    
    def get_all_methods(self, assembly: Any) -> list:
        """Get all methods from assembly."""
        methods = []
        if hasattr(assembly, 'net') and assembly.net:
            if hasattr(assembly.net, 'metadata'):
                metadata = assembly.net.metadata
                if hasattr(metadata, 'netmetadata'):
                    for row in metadata.netmetadata.tables.MethodDef:
                        methods.append(row)
        return methods

