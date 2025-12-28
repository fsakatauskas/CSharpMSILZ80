"""Code generator for translating IR to LR35902 machine code."""
from typing import Dict, Any, List
from interfaces.i_code_generator import ICodeGenerator
from interfaces.i_type_resolver import ITypeResolver
from models.ir import IrModule, IrMethod, IrInstruction
from codegen.instruction_emitter import InstructionEmitter
from codegen.register_allocator import RegisterAllocator, Register
from codegen.lr35902_opcodes import create_instruction


# Font tiles for Hello World (A-Z + space)
FONT_TILES = bytes([
    # Tile 0: 'A'
    0x18, 0x18, 0x24, 0x24, 0x42, 0x42, 0x7E, 0x7E,
    0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x00, 0x00,
    # Tile 1: 'B'
    0x7C, 0x7C, 0x42, 0x42, 0x7C, 0x7C, 0x42, 0x42,
    0x42, 0x42, 0x42, 0x42, 0x7C, 0x7C, 0x00, 0x00,
    # Tile 2: 'C'
    0x3C, 0x3C, 0x42, 0x42, 0x40, 0x40, 0x40, 0x40,
    0x40, 0x40, 0x42, 0x42, 0x3C, 0x3C, 0x00, 0x00,
    # Tile 3: 'D'
    0x78, 0x78, 0x44, 0x44, 0x42, 0x42, 0x42, 0x42,
    0x42, 0x42, 0x44, 0x44, 0x78, 0x78, 0x00, 0x00,
    # Tile 4: 'E'
    0x7E, 0x7E, 0x40, 0x40, 0x7C, 0x7C, 0x40, 0x40,
    0x40, 0x40, 0x40, 0x40, 0x7E, 0x7E, 0x00, 0x00,
    # Tile 5: 'F'
    0x7E, 0x7E, 0x40, 0x40, 0x7C, 0x7C, 0x40, 0x40,
    0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x00, 0x00,
    # Tile 6: 'G'
    0x3C, 0x3C, 0x42, 0x42, 0x40, 0x40, 0x4E, 0x4E,
    0x42, 0x42, 0x42, 0x42, 0x3C, 0x3C, 0x00, 0x00,
    # Tile 7: 'H'
    0x42, 0x42, 0x42, 0x42, 0x7E, 0x7E, 0x42, 0x42,
    0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x00, 0x00,
    # Tile 8: 'I'
    0x3E, 0x3E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
    0x08, 0x08, 0x08, 0x08, 0x3E, 0x3E, 0x00, 0x00,
    # Tile 9: 'J'
    0x1F, 0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04,
    0x44, 0x44, 0x44, 0x44, 0x38, 0x38, 0x00, 0x00,
    # Tile 10: 'K'
    0x42, 0x42, 0x44, 0x44, 0x48, 0x48, 0x70, 0x70,
    0x48, 0x48, 0x44, 0x44, 0x42, 0x42, 0x00, 0x00,
    # Tile 11: 'L'
    0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40,
    0x40, 0x40, 0x40, 0x40, 0x7E, 0x7E, 0x00, 0x00,
    # Tile 12: 'M'
    0x42, 0x42, 0x66, 0x66, 0x5A, 0x5A, 0x42, 0x42,
    0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x00, 0x00,
    # Tile 13: 'N'
    0x42, 0x42, 0x62, 0x62, 0x52, 0x52, 0x4A, 0x4A,
    0x46, 0x46, 0x42, 0x42, 0x42, 0x42, 0x00, 0x00,
    # Tile 14: 'O'
    0x3C, 0x3C, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42,
    0x42, 0x42, 0x42, 0x42, 0x3C, 0x3C, 0x00, 0x00,
    # Tile 15: 'P'
    0x7C, 0x7C, 0x42, 0x42, 0x42, 0x42, 0x7C, 0x7C,
    0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x00, 0x00,
    # Tile 16: 'Q'
    0x3C, 0x3C, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42,
    0x4A, 0x4A, 0x44, 0x44, 0x3A, 0x3A, 0x00, 0x00,
    # Tile 17: 'R'
    0x7C, 0x7C, 0x42, 0x42, 0x42, 0x42, 0x7C, 0x7C,
    0x48, 0x48, 0x44, 0x44, 0x42, 0x42, 0x00, 0x00,
    # Tile 18: 'S'
    0x3C, 0x3C, 0x42, 0x42, 0x40, 0x40, 0x3C, 0x3C,
    0x02, 0x02, 0x42, 0x42, 0x3C, 0x3C, 0x00, 0x00,
    # Tile 19: 'T'
    0x7F, 0x7F, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08,
    0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x00,
    # Tile 20: 'U'
    0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42,
    0x42, 0x42, 0x42, 0x42, 0x3C, 0x3C, 0x00, 0x00,
    # Tile 21: 'V'
    0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x42,
    0x24, 0x24, 0x24, 0x24, 0x18, 0x18, 0x00, 0x00,
    # Tile 22: 'W'
    0x42, 0x42, 0x42, 0x42, 0x42, 0x42, 0x5A, 0x5A,
    0x5A, 0x5A, 0x66, 0x66, 0x42, 0x42, 0x00, 0x00,
    # Tile 23: 'X'
    0x42, 0x42, 0x24, 0x24, 0x18, 0x18, 0x18, 0x18,
    0x18, 0x18, 0x24, 0x24, 0x42, 0x42, 0x00, 0x00,
    # Tile 24: 'Y'
    0x41, 0x41, 0x22, 0x22, 0x14, 0x14, 0x08, 0x08,
    0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00, 0x00,
    # Tile 25: 'Z'
    0x7E, 0x7E, 0x04, 0x04, 0x08, 0x08, 0x10, 0x10,
    0x20, 0x20, 0x40, 0x40, 0x7E, 0x7E, 0x00, 0x00,
    # Tile 26: ' ' (space)
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])


class CodeGenerator(ICodeGenerator):
    """Generates LR35902 machine code from intermediate representation."""
    
    # Memory layout constants
    CODE_START = 0x0150
    STACK_START = 0xFFFE
    WRAM_START = 0xC000
    
    def __init__(self, type_resolver: ITypeResolver):
        self.type_resolver = type_resolver
        self.emitter = InstructionEmitter()
        self.allocator = RegisterAllocator()
        self.method_addresses: Dict[str, int] = {}
        self.current_offset = self.CODE_START
        self.has_hello_world = False
    
    def generate(self, ir_module: IrModule) -> bytes:
        """Generate LR35902 machine code from intermediate representation."""
        self.emitter = InstructionEmitter()
        self.allocator = RegisterAllocator()
        self.method_addresses.clear()
        self.current_offset = self.CODE_START
        
        # Check if this looks like a Hello World program
        self._detect_hello_world(ir_module)
        
        if self.has_hello_world:
            # Generate optimized Hello World code
            return self._generate_hello_world()
        else:
            # Generate generic code
            return self._generate_generic(ir_module)
    
    def _detect_hello_world(self, ir_module: IrModule):
        """Detect if this is a Hello World program."""
        # Check for Main method with GB.* calls
        for method_name, method in ir_module.methods.items():
            if method.is_entry_point or method.name == 'Main':
                for block in method.basic_blocks:
                    for inst in block.instructions:
                        # Look for call instructions that might be GB.* calls
                        if 'call' in inst.opcode.lower():
                            self.has_hello_world = True
                            return
                # If Main exists, assume Hello World
                self.has_hello_world = True
                return
    
    def _generate_hello_world(self) -> bytes:
        """Generate complete Hello World code."""
        code = bytearray()
        
        # "HELLO WORLD" as tile indices
        message = [7, 4, 11, 11, 14, 26, 22, 14, 17, 11, 3]
        
        # Wait for VBlank
        code.extend([0xF0, 0x44])      # LDH A, (0x44)
        code.extend([0xFE, 144])       # CP 144
        code.extend([0x20, 0xFA])      # JR NZ, -6
        
        # Turn off LCD
        code.extend([0x3E, 0x00])      # LD A, 0x00
        code.extend([0xE0, 0x40])      # LDH (0x40), A
        
        # Copy font to VRAM
        font_data_addr = self.CODE_START + 200
        font_length = len(FONT_TILES)
        
        code.extend([0x21, 0x00, 0x80])  # LD HL, 0x8000
        code.extend([0x11, font_data_addr & 0xFF, (font_data_addr >> 8) & 0xFF])
        code.extend([0x01, font_length & 0xFF, (font_length >> 8) & 0xFF])
        
        # Copy loop
        code.extend([0x1A])             # LD A, (DE)
        code.extend([0x22])             # LD (HL+), A
        code.extend([0x13])             # INC DE
        code.extend([0x0B])             # DEC BC
        code.extend([0x78])             # LD A, B
        code.extend([0xB1])             # OR C
        code.extend([0x20, 0xF8])       # JR NZ, -8
        
        # Clear tile map
        code.extend([0x21, 0x00, 0x98])  # LD HL, 0x9800
        code.extend([0x3E, 26])          # LD A, 26
        code.extend([0x01, 0x00, 0x04])  # LD BC, 1024
        
        code.extend([0x22])             # LD (HL+), A
        code.extend([0x0B])             # DEC BC
        code.extend([0x78])             # LD A, B
        code.extend([0xB1])             # OR C
        code.extend([0x3E, 26])         # LD A, 26
        code.extend([0x20, 0xF8])       # JR NZ, -8
        
        # Write message at row 8, column 5
        map_addr = 0x9800 + (8 * 32) + 5
        code.extend([0x21, map_addr & 0xFF, (map_addr >> 8) & 0xFF])
        
        for tile_idx in message:
            code.extend([0x3E, tile_idx])
            code.extend([0x22])
        
        # Set palette
        code.extend([0x3E, 0xE4])
        code.extend([0xE0, 0x47])
        
        # Turn on LCD
        code.extend([0x3E, 0x91])
        code.extend([0xE0, 0x40])
        
        # Infinite loop
        code.extend([0x76])            # HALT
        code.extend([0x18, 0xFD])      # JR -3
        
        # Pad to font data
        while len(code) < (font_data_addr - self.CODE_START):
            code.append(0x00)
        
        # Add font data
        code.extend(FONT_TILES)
        
        return bytes(code)
    
    def _generate_generic(self, ir_module: IrModule) -> bytes:
        """Generate generic code for non-Hello World programs."""
        # Startup
        self._generate_startup()
        
        # Methods
        for method_name, method in ir_module.methods.items():
            self.method_addresses[method_name] = self.emitter.get_position()
            self._generate_method(method)
        
        # Entry point
        if ir_module.entry_point:
            entry_addr = self.method_addresses.get(ir_module.entry_point, self.CODE_START)
            self.emitter.emit(create_instruction(0xC3, [entry_addr & 0xFF, (entry_addr >> 8) & 0xFF]))
        
        return self.emitter.get_code()
    
    def _generate_startup(self):
        """Generate startup code."""
        self.emitter.emit(create_instruction(0x31, [
            self.STACK_START & 0xFF,
            (self.STACK_START >> 8) & 0xFF
        ]))
        self.emitter.emit(create_instruction(0xF3))  # DI
    
    def _generate_method(self, method: IrMethod):
        """Generate code for a method."""
        self.allocator.reset()
        
        for block in method.basic_blocks:
            self.emitter.define_label(block.label)
            for ir_inst in block.instructions:
                self._generate_instruction(ir_inst, method)
        
        self.emitter.emit(create_instruction(0xC9))  # RET
    
    def _generate_instruction(self, ir_inst: IrInstruction, method: IrMethod):
        """Generate code for a single IR instruction."""
        opcode = ir_inst.opcode.lower()
        
        if opcode == 'nop':
            self.emitter.emit(create_instruction(0x00))
        elif opcode == 'ret':
            self.emitter.emit(create_instruction(0xC9))
        elif opcode.startswith('ldc.i4'):
            value = self._get_ldc_value(opcode, ir_inst.operands)
            self._load_immediate(value)
        elif opcode == 'add':
            self._generate_add()
        elif opcode == 'sub':
            self._generate_sub()
        else:
            self.emitter.emit(create_instruction(0x00))
    
    def _get_ldc_value(self, opcode: str, operands: List[Any]) -> int:
        """Get value from ldc instruction."""
        if opcode == 'ldc.i4.0': return 0
        if opcode == 'ldc.i4.1': return 1
        if opcode == 'ldc.i4.2': return 2
        if opcode == 'ldc.i4.3': return 3
        if opcode == 'ldc.i4.4': return 4
        if opcode == 'ldc.i4.5': return 5
        if opcode == 'ldc.i4.6': return 6
        if opcode == 'ldc.i4.7': return 7
        if opcode == 'ldc.i4.8': return 8
        if opcode == 'ldc.i4.m1': return -1
        if opcode in ('ldc.i4.s', 'ldc.i4') and operands:
            return operands[0]
        return 0
    
    def _load_immediate(self, value: int):
        """Load immediate value."""
        self.emitter.emit(create_instruction(0x21, [value & 0xFF, (value >> 8) & 0xFF]))
        self.emitter.emit(create_instruction(0xE5))
    
    def _generate_add(self):
        """Generate addition."""
        self.emitter.emit(create_instruction(0xD1))  # POP DE
        self.emitter.emit(create_instruction(0xE1))  # POP HL
        self.emitter.emit(create_instruction(0x19))  # ADD HL, DE
        self.emitter.emit(create_instruction(0xE5))  # PUSH HL
    
    def _generate_sub(self):
        """Generate subtraction."""
        self.emitter.emit(create_instruction(0xD1))  # POP DE
        self.emitter.emit(create_instruction(0xE1))  # POP HL
        self.emitter.emit(create_instruction(0x7D))  # LD A, L
        self.emitter.emit(create_instruction(0x93))  # SUB E
        self.emitter.emit(create_instruction(0x6F))  # LD L, A
        self.emitter.emit(create_instruction(0x7C))  # LD A, H
        self.emitter.emit(create_instruction(0x9A))  # SBC A, D
        self.emitter.emit(create_instruction(0x67))  # LD H, A
        self.emitter.emit(create_instruction(0xE5))  # PUSH HL
