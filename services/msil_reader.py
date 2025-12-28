"""MSIL reader service for parsing .NET assemblies."""
import dnfile
from typing import Any, Optional, List
from interfaces.i_msil_reader import IMsilReader


class MsilReader(IMsilReader):
    """Reads and parses .NET assemblies using dnfile."""
    
    def read_assembly(self, path: str) -> Any:
        """
        Read and parse a .NET assembly file.
        
        Args:
            path: Path to the .NET assembly (.dll) file
            
        Returns:
            Parsed assembly object (dnfile.dnPE object)
        """
        try:
            pe = dnfile.dnPE(path)
            return pe
        except Exception as e:
            raise ValueError(f"Failed to read assembly {path}: {e}")
    
    def get_entry_point(self, assembly: Any) -> Optional[Any]:
        """Get the entry point method from assembly."""
        # Find method named "Main"
        methods = self.get_all_methods(assembly)
        for method in methods:
            if hasattr(method, 'Name') and method.Name == 'Main':
                return method
        return None
    
    def get_all_types(self, assembly: Any) -> List[Any]:
        """Get all types from assembly."""
        types = []
        if hasattr(assembly, 'net') and assembly.net:
            if hasattr(assembly.net, 'mdtables') and assembly.net.mdtables:
                if assembly.net.mdtables.TypeDef:
                    for row in assembly.net.mdtables.TypeDef:
                        types.append(row)
        return types
    
    def get_all_methods(self, assembly: Any) -> List[Any]:
        """Get all methods from assembly."""
        methods = []
        if hasattr(assembly, 'net') and assembly.net:
            if hasattr(assembly.net, 'mdtables') and assembly.net.mdtables:
                if assembly.net.mdtables.MethodDef:
                    for row in assembly.net.mdtables.MethodDef:
                        methods.append(row)
        return methods
    
    def get_method_body(self, assembly: Any, method: Any) -> Optional[bytes]:
        """Get the IL bytecode for a method."""
        if hasattr(method, 'Rva') and method.Rva:
            try:
                # Get the method body from the RVA
                rva = method.Rva
                # Read the method body header and IL bytes
                body_offset = assembly.get_offset_from_rva(rva)
                data = assembly.__data__
                
                # Parse method header (tiny or fat)
                header_byte = data[body_offset]
                
                if (header_byte & 0x03) == 0x02:
                    # Tiny header: 1 byte, code size in upper 6 bits
                    code_size = header_byte >> 2
                    il_start = body_offset + 1
                    return bytes(data[il_start:il_start + code_size])
                elif (header_byte & 0x03) == 0x03:
                    # Fat header: 12 bytes
                    flags = header_byte | (data[body_offset + 1] << 8)
                    max_stack = data[body_offset + 2] | (data[body_offset + 3] << 8)
                    code_size = (data[body_offset + 4] | 
                                (data[body_offset + 5] << 8) |
                                (data[body_offset + 6] << 16) |
                                (data[body_offset + 7] << 24))
                    il_start = body_offset + 12
                    return bytes(data[il_start:il_start + code_size])
            except Exception as e:
                print(f"Warning: Could not read method body: {e}")
                return None
        return None
    
    def get_user_strings(self, assembly: Any) -> dict:
        """Get user strings from the #US heap."""
        strings = {}
        if hasattr(assembly, 'net') and assembly.net:
            if hasattr(assembly.net, 'user_strings') and assembly.net.user_strings:
                for idx, s in enumerate(assembly.net.user_strings):
                    strings[idx] = s
        return strings
    
    def get_type_by_name(self, assembly: Any, name: str) -> Optional[Any]:
        """Get a type by name."""
        types = self.get_all_types(assembly)
        for t in types:
            if hasattr(t, 'TypeName') and t.TypeName == name:
                return t
            full_name = f"{t.TypeNamespace}.{t.TypeName}" if t.TypeNamespace else t.TypeName
            if full_name == name:
                return t
        return None
