"""IR builder service for converting MSIL to intermediate representation."""
from typing import Any, List, Optional
from interfaces.i_ir_builder import IIrBuilder
from interfaces.i_msil_reader import IMsilReader
from models.ir import IrModule, IrMethod, IrType, IrBasicBlock, IrInstruction


# MSIL Opcodes (common ones)
MSIL_OPCODES = {
    0x00: 'nop',
    0x01: 'break',
    0x02: 'ldarg.0',
    0x03: 'ldarg.1',
    0x04: 'ldarg.2',
    0x05: 'ldarg.3',
    0x06: 'ldloc.0',
    0x07: 'ldloc.1',
    0x08: 'ldloc.2',
    0x09: 'ldloc.3',
    0x0A: 'stloc.0',
    0x0B: 'stloc.1',
    0x0C: 'stloc.2',
    0x0D: 'stloc.3',
    0x0E: 'ldarg.s',
    0x0F: 'ldarga.s',
    0x10: 'starg.s',
    0x11: 'ldloc.s',
    0x12: 'ldloca.s',
    0x13: 'stloc.s',
    0x14: 'ldnull',
    0x15: 'ldc.i4.m1',
    0x16: 'ldc.i4.0',
    0x17: 'ldc.i4.1',
    0x18: 'ldc.i4.2',
    0x19: 'ldc.i4.3',
    0x1A: 'ldc.i4.4',
    0x1B: 'ldc.i4.5',
    0x1C: 'ldc.i4.6',
    0x1D: 'ldc.i4.7',
    0x1E: 'ldc.i4.8',
    0x1F: 'ldc.i4.s',
    0x20: 'ldc.i4',
    0x21: 'ldc.i8',
    0x22: 'ldc.r4',
    0x23: 'ldc.r8',
    0x25: 'dup',
    0x26: 'pop',
    0x27: 'jmp',
    0x28: 'call',
    0x29: 'calli',
    0x2A: 'ret',
    0x2B: 'br.s',
    0x2C: 'brfalse.s',
    0x2D: 'brtrue.s',
    0x2E: 'beq.s',
    0x2F: 'bge.s',
    0x30: 'bgt.s',
    0x31: 'ble.s',
    0x32: 'blt.s',
    0x38: 'br',
    0x39: 'brfalse',
    0x3A: 'brtrue',
    0x58: 'add',
    0x59: 'sub',
    0x5A: 'mul',
    0x5B: 'div',
    0x5F: 'and',
    0x60: 'or',
    0x61: 'xor',
    0x62: 'shl',
    0x63: 'shr',
    0x6F: 'callvirt',
    0x72: 'ldstr',
    0x73: 'newobj',
    0x7B: 'ldfld',
    0x7C: 'ldflda',
    0x7D: 'stfld',
    0x7E: 'ldsfld',
    0x7F: 'ldsflda',
    0x80: 'stsfld',
    0x8C: 'box',
    0x8D: 'newarr',
    0x8E: 'ldlen',
    0x8F: 'ldelema',
    0x90: 'ldelem.i1',
    0x91: 'ldelem.u1',
    0x92: 'ldelem.i2',
    0x93: 'ldelem.u2',
    0x94: 'ldelem.i4',
    0x95: 'ldelem.u4',
    0x96: 'ldelem.i8',
    0x97: 'ldelem.i',
    0x98: 'ldelem.r4',
    0x99: 'ldelem.r8',
    0x9A: 'ldelem.ref',
    0x9C: 'stelem.i1',
    0x9D: 'stelem.i2',
    0x9E: 'stelem.i4',
    0x9F: 'stelem.i8',
    0xA0: 'stelem.r4',
    0xA1: 'stelem.r8',
    0xA2: 'stelem.ref',
    0xD0: 'ldtoken',
    0xD1: 'conv.u2',
    0xD2: 'conv.u1',
    0xD3: 'conv.i',
}


class IrBuilder(IIrBuilder):
    """Builds intermediate representation from parsed assembly."""
    
    def __init__(self, msil_reader: IMsilReader):
        self.msil_reader = msil_reader
    
    def build(self, assembly: Any) -> IrModule:
        """
        Build intermediate representation from parsed assembly.
        """
        module_name = getattr(assembly, 'filename', 'Unknown')
        ir_module = IrModule(name=module_name)
        
        # Extract types
        types = self.msil_reader.get_all_types(assembly)
        for type_def in types:
            type_name = self._get_type_name(type_def)
            
            # Skip internal types
            if type_name.startswith('<') or type_name == '<Module>':
                continue
            
            ir_type = IrType(
                name=type_name.split('.')[-1],
                full_name=type_name,
                is_struct=False,
                is_class=True,
                is_primitive=self._is_primitive(type_name),
            )
            ir_module.types[type_name] = ir_type
        
        # Extract methods
        methods = self.msil_reader.get_all_methods(assembly)
        
        for method_def in methods:
            method_name = self._get_method_name(method_def)
            
            # Skip constructor methods for now
            if method_name.startswith('.'):
                continue
                
            full_name = self._get_method_full_name(method_def)
            is_entry = (method_name == 'Main')
            
            ir_method = IrMethod(
                name=method_name,
                full_name=full_name,
                is_static=True,  # Assume static for now
                is_entry_point=is_entry,
            )
            
            # Extract method body
            body = self.msil_reader.get_method_body(assembly, method_def)
            if body:
                self._parse_il_body(ir_method, body, assembly)
            
            ir_module.methods[full_name] = ir_method
            
            if is_entry:
                ir_module.entry_point = full_name
        
        return ir_module
    
    def _parse_il_body(self, ir_method: IrMethod, il_bytes: bytes, assembly: Any):
        """Parse IL bytecode into IR instructions."""
        block = IrBasicBlock(label="entry")
        
        i = 0
        while i < len(il_bytes):
            opcode = il_bytes[i]
            
            # Handle two-byte opcodes (0xFE prefix)
            if opcode == 0xFE:
                i += 1
                if i < len(il_bytes):
                    opcode = 0xFE00 | il_bytes[i]
            
            opcode_name = MSIL_OPCODES.get(opcode & 0xFF, f'unknown_{opcode:02x}')
            operands = []
            
            # Parse operands based on opcode
            i += 1
            
            if opcode_name in ('ldc.i4.s', 'ldarg.s', 'ldloc.s', 'stloc.s', 'starg.s'):
                # 1-byte operand
                if i < len(il_bytes):
                    operands.append(il_bytes[i])
                    i += 1
            elif opcode_name in ('ldc.i4', 'br', 'brfalse', 'brtrue', 'call', 'callvirt', 
                                 'newobj', 'ldfld', 'stfld', 'ldsfld', 'stsfld', 'ldstr',
                                 'newarr', 'ldtoken'):
                # 4-byte operand
                if i + 3 < len(il_bytes):
                    operand = (il_bytes[i] | 
                              (il_bytes[i+1] << 8) | 
                              (il_bytes[i+2] << 16) | 
                              (il_bytes[i+3] << 24))
                    operands.append(operand)
                    i += 4
            elif opcode_name in ('br.s', 'brfalse.s', 'brtrue.s', 'beq.s', 'bge.s', 
                                 'bgt.s', 'ble.s', 'blt.s'):
                # 1-byte signed offset
                if i < len(il_bytes):
                    offset = il_bytes[i]
                    if offset > 127:
                        offset -= 256
                    operands.append(offset)
                    i += 1
            
            ir_inst = IrInstruction(
                opcode=opcode_name,
                operands=operands,
                metadata={'raw_opcode': opcode}
            )
            block.instructions.append(ir_inst)
        
        ir_method.basic_blocks.append(block)
    
    def _get_type_name(self, type_def: Any) -> str:
        """Extract type name."""
        namespace = getattr(type_def, 'TypeNamespace', '') or ''
        name = getattr(type_def, 'TypeName', str(type_def))
        # Convert HeapItemString to str
        namespace = str(namespace) if namespace else ''
        name = str(name) if name else ''
        if namespace:
            return f"{namespace}.{name}"
        return name
    
    def _get_method_name(self, method_def: Any) -> str:
        """Extract method name."""
        name = getattr(method_def, 'Name', str(method_def))
        return str(name) if name else ''
    
    def _get_method_full_name(self, method_def: Any) -> str:
        """Extract full method name."""
        name = getattr(method_def, 'Name', str(method_def))
        return str(name) if name else ''
    
    def _is_primitive(self, type_name: str) -> bool:
        """Check if type is primitive."""
        primitives = [
            'System.Byte', 'System.SByte', 'System.Boolean',
            'System.Int16', 'System.UInt16', 'System.Int32', 'System.UInt32',
            'System.Char', 'System.Single', 'System.Double',
        ]
        return type_name in primitives
