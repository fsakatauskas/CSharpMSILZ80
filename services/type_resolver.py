"""Type resolver for mapping C# types to Game Boy memory layouts."""
from typing import Dict, Any, Optional
from interfaces.i_type_resolver import ITypeResolver


class TypeResolver(ITypeResolver):
    """Maps C# types to Game Boy memory layouts."""
    
    # Primitive type sizes
    PRIMITIVE_SIZES = {
        'System.Byte': 1,
        'System.SByte': 1,
        'System.Boolean': 1,
        'System.Int16': 2,
        'System.UInt16': 2,
        'System.Int32': 4,
        'System.UInt32': 4,
        'System.IntPtr': 2,  # 16-bit pointer on GB
        'System.UIntPtr': 2,
    }
    
    def __init__(self):
        self.type_cache: Dict[str, Dict[str, Any]] = {}
    
    def resolve_type(self, csharp_type: Any) -> Dict[str, Any]:
        """
        Resolve a C# type to its Game Boy memory layout.
        
        Args:
            csharp_type: C# type from assembly (dnfile type object)
            
        Returns:
            Dictionary with size, alignment, and layout information
        """
        type_name = self._get_type_name(csharp_type)
        
        if type_name in self.type_cache:
            return self.type_cache[type_name]
        
        # Check if primitive
        if type_name in self.PRIMITIVE_SIZES:
            size = self.PRIMITIVE_SIZES[type_name]
            layout = {
                'name': type_name,
                'size': size,
                'alignment': size,
                'is_primitive': True,
                'is_struct': False,
                'is_class': False,
                'fields': [],
            }
            self.type_cache[type_name] = layout
            return layout
        
        # Handle arrays
        if hasattr(csharp_type, 'is_array') and csharp_type.is_array:
            element_type = self.resolve_type(csharp_type.element_type)
            layout = {
                'name': type_name,
                'size': 2,  # Pointer to array data
                'alignment': 2,
                'is_primitive': False,
                'is_struct': False,
                'is_class': False,
                'is_array': True,
                'element_type': element_type,
                'element_size': element_type['size'],
            }
            self.type_cache[type_name] = layout
            return layout
        
        # Handle structs and classes
        size = 0
        fields = []
        
        if hasattr(csharp_type, 'fields'):
            for field in csharp_type.fields:
                if field.is_literal:  # Skip constants
                    continue
                
                field_type = self.resolve_type(field.type)
                field_size = field_type['size']
                field_info = {
                    'name': field.name,
                    'type': field_type,
                    'offset': size,
                    'size': field_size,
                }
                fields.append(field_info)
                size += field_size
        
        # Ensure minimum size of 1 byte
        if size == 0:
            size = 1
        
        layout = {
            'name': type_name,
            'size': size,
            'alignment': 1,  # GB has no strict alignment requirements
            'is_primitive': False,
            'is_struct': hasattr(csharp_type, 'is_value_type') and csharp_type.is_value_type,
            'is_class': not (hasattr(csharp_type, 'is_value_type') and csharp_type.is_value_type),
            'fields': fields,
        }
        
        self.type_cache[type_name] = layout
        return layout
    
    def get_type_size(self, csharp_type: Any) -> int:
        """Get the size in bytes of a C# type on Game Boy."""
        layout = self.resolve_type(csharp_type)
        return layout['size']
    
    def _get_type_name(self, csharp_type: Any) -> str:
        """Extract type name from dnfile type object."""
        if hasattr(csharp_type, 'fullname'):
            return csharp_type.fullname
        if hasattr(csharp_type, 'name'):
            return csharp_type.name
        return str(csharp_type)

