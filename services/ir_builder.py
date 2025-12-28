"""IR builder service for converting MSIL to intermediate representation."""
from typing import Any, List
from interfaces.i_ir_builder import IIrBuilder
from interfaces.i_msil_reader import IMsilReader
from models.ir import IrModule, IrMethod, IrType, IrBasicBlock, IrInstruction


class IrBuilder(IIrBuilder):
    """Builds intermediate representation from parsed assembly."""
    
    def __init__(self, msil_reader: IMsilReader):
        self.msil_reader = msil_reader
    
    def build(self, assembly: Any) -> IrModule:
        """
        Build intermediate representation from parsed assembly.
        
        Args:
            assembly: Parsed .NET assembly
            
        Returns:
            IR module containing methods, types, etc.
        """
        module_name = getattr(assembly, 'filename', 'Unknown')
        ir_module = IrModule(name=module_name)
        
        # Extract types
        types = self.msil_reader.get_all_types(assembly)
        for type_def in types:
            type_name = self._get_type_name(type_def)
            ir_type = IrType(
                name=type_name.split('.')[-1],
                full_name=type_name,
                is_struct=getattr(type_def, 'is_value_type', False),
                is_class=not getattr(type_def, 'is_value_type', False),
                is_primitive=self._is_primitive(type_name),
            )
            ir_module.types[type_name] = ir_type
        
        # Extract methods
        methods = self.msil_reader.get_all_methods(assembly)
        entry_point = self.msil_reader.get_entry_point(assembly)
        
        for method_def in methods:
            method_name = self._get_method_name(method_def)
            full_name = self._get_method_full_name(method_def)
            
            # Check if this is the entry point
            is_entry = False
            if entry_point:
                entry_name = self._get_method_full_name(entry_point)
                is_entry = (full_name == entry_name or 
                           method_name == 'Main')
            
            ir_method = IrMethod(
                name=method_name,
                full_name=full_name,
                is_static=getattr(method_def, 'is_static', True),
                is_entry_point=is_entry,
            )
            
            # Extract method body if available
            if hasattr(method_def, 'body') and method_def.body:
                self._build_method_body(ir_method, method_def.body)
            
            ir_module.methods[full_name] = ir_method
            
            if is_entry:
                ir_module.entry_point = full_name
        
        return ir_module
    
    def _build_method_body(self, ir_method: IrMethod, method_body: Any):
        """Build IR for method body."""
        # Create a single basic block for now
        # In a full implementation, we'd analyze control flow
        block = IrBasicBlock(label="entry")
        
        # Extract local variables
        if hasattr(method_body, 'local_vars'):
            for local in method_body.local_vars:
                ir_method.local_variables.append(local)
        
        # Extract instructions
        if hasattr(method_body, 'instructions'):
            for msil_inst in method_body.instructions:
                ir_inst = IrInstruction(
                    opcode=msil_inst.opcode.name if hasattr(msil_inst.opcode, 'name') else str(msil_inst.opcode),
                    operands=list(msil_inst.operands) if hasattr(msil_inst, 'operands') else [],
                )
                block.instructions.append(ir_inst)
        
        ir_method.basic_blocks.append(block)
    
    def _get_type_name(self, type_def: Any) -> str:
        """Extract type name."""
        if hasattr(type_def, 'fullname'):
            return type_def.fullname
        if hasattr(type_def, 'name'):
            return type_def.name
        return str(type_def)
    
    def _get_method_name(self, method_def: Any) -> str:
        """Extract method name."""
        if hasattr(method_def, 'name'):
            return method_def.name
        return str(method_def)
    
    def _get_method_full_name(self, method_def: Any) -> str:
        """Extract full method name."""
        if hasattr(method_def, 'fullname'):
            return method_def.fullname
        if hasattr(method_def, 'name'):
            return method_def.name
        return str(method_def)
    
    def _is_primitive(self, type_name: str) -> bool:
        """Check if type is primitive."""
        primitives = [
            'System.Byte', 'System.SByte', 'System.Boolean',
            'System.Int16', 'System.UInt16', 'System.Int32', 'System.UInt32',
            'System.Char', 'System.Single', 'System.Double',
        ]
        return type_name in primitives

