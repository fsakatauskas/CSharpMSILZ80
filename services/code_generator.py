"""Code generator for translating IR to LR35902 machine code."""
from typing import Dict, Any
from interfaces.i_code_generator import ICodeGenerator
from interfaces.i_type_resolver import ITypeResolver
from models.ir import IrModule, IrMethod, IrInstruction
from codegen.instruction_emitter import InstructionEmitter
from codegen.register_allocator import RegisterAllocator, Register
from codegen.lr35902_opcodes import create_instruction


class CodeGenerator(ICodeGenerator):
    """Generates LR35902 machine code from intermediate representation."""
    
    # Memory layout constants
    CODE_START = 0x0150  # After cartridge header
    STACK_START = 0xFFFE  # Stack grows downward
    WRAM_START = 0xC000  # Work RAM
    
    def __init__(self, type_resolver: ITypeResolver):
        self.type_resolver = type_resolver
        self.emitter = InstructionEmitter()
        self.allocator = RegisterAllocator()
        self.method_addresses: Dict[str, int] = {}
        self.current_offset = self.CODE_START
    
    def generate(self, ir_module: IrModule) -> bytes:
        """
        Generate LR35902 machine code from intermediate representation.
        
        Args:
            ir_module: Intermediate representation module
            
        Returns:
            Raw machine code bytes
        """
        self.emitter = InstructionEmitter()
        self.allocator = RegisterAllocator()
        self.method_addresses.clear()
        self.current_offset = self.CODE_START
        
        # Generate startup code
        self._generate_startup()
        
        # Generate all methods
        for method_name, method in ir_module.methods.items():
            self.method_addresses[method_name] = self.emitter.get_position()
            self._generate_method(method)
        
        # Generate entry point jump
        if ir_module.entry_point:
            entry_addr = self.method_addresses.get(ir_module.entry_point, self.CODE_START)
            # Jump to entry point
            self.emitter.emit(create_instruction(0xC3, [entry_addr & 0xFF, (entry_addr >> 8) & 0xFF]))
        
        return self.emitter.get_code()
    
    def _generate_startup(self):
        """Generate startup/bootstrap code."""
        # Initialize stack pointer
        # LD SP, STACK_START
        self.emitter.emit(create_instruction(0x31, [
            self.STACK_START & 0xFF,
            (self.STACK_START >> 8) & 0xFF
        ]))
        
        # Disable interrupts initially
        # DI (disable interrupts) - opcode 0xF3
        self.emitter.emit(create_instruction(0xF3))
    
    def _generate_method(self, method: IrMethod):
        """Generate code for a method."""
        self.allocator.reset()
        
        # Method prologue: save frame
        # For now, simple implementation
        # In full implementation, we'd set up stack frame
        
        # Generate code for each basic block
        for block in method.basic_blocks:
            self.emitter.define_label(block.label)
            
            for ir_inst in block.instructions:
                self._generate_instruction(ir_inst, method)
        
        # Method epilogue: restore and return
        # RET
        self.emitter.emit(create_instruction(0xC9))
    
    def _generate_instruction(self, ir_inst: IrInstruction, method: IrMethod):
        """Generate code for a single IR instruction."""
        opcode_name = ir_inst.opcode.upper()
        
        # Map common MSIL opcodes to LR35902
        if opcode_name == 'NOP':
            self.emitter.emit(create_instruction(0x00))
        
        elif opcode_name == 'RET' or opcode_name == 'RETURN':
            self.emitter.emit(create_instruction(0xC9))
        
        elif opcode_name.startswith('LDC_I4'):
            # Load constant integer
            value = ir_inst.operands[0] if ir_inst.operands else 0
            self._load_immediate(value)
        
        elif opcode_name.startswith('LDARG'):
            # Load argument
            arg_index = int(ir_inst.operands[0]) if ir_inst.operands else 0
            self._load_argument(arg_index, method)
        
        elif opcode_name.startswith('LDLOC'):
            # Load local variable
            local_index = int(ir_inst.operands[0]) if ir_inst.operands else 0
            self._load_local(local_index, method)
        
        elif opcode_name.startswith('STLOC'):
            # Store local variable
            local_index = int(ir_inst.operands[0]) if ir_inst.operands else 0
            self._store_local(local_index, method)
        
        elif opcode_name == 'ADD':
            self._generate_add()
        
        elif opcode_name == 'SUB':
            self._generate_sub()
        
        elif opcode_name == 'MUL':
            # Multiplication requires runtime call
            self._generate_mul_call()
        
        elif opcode_name == 'DIV':
            # Division requires runtime call
            self._generate_div_call()
        
        elif opcode_name.startswith('CALL'):
            # Method call
            if ir_inst.operands:
                method_name = str(ir_inst.operands[0])
                self._generate_call(method_name)
        
        elif opcode_name.startswith('BR') or opcode_name.startswith('BRFALSE') or opcode_name.startswith('BRTRUE'):
            # Branch instruction
            target = ir_inst.operands[0] if ir_inst.operands else None
            if target:
                self._generate_branch(opcode_name, target)
        
        else:
            # Unknown opcode - emit NOP as placeholder
            self.emitter.emit(create_instruction(0x00))
    
    def _load_immediate(self, value: int):
        """Load immediate value into HL."""
        # LD HL, value
        self.emitter.emit(create_instruction(0x21, [
            value & 0xFF,
            (value >> 8) & 0xFF
        ]))
        # PUSH HL
        self.emitter.emit(create_instruction(0xE5))
    
    def _load_argument(self, index: int, method: IrMethod):
        """Load method argument."""
        # Arguments are on stack above return address
        # For now, simplified: assume args are at SP+2, SP+4, etc.
        offset = 2 + (index * 2)
        # POP return address temporarily, load arg, push back
        # Simplified: load from stack frame
        # LD HL, (SP+offset)
        # This is complex, so for now use a placeholder
        self.emitter.emit(create_instruction(0x00))  # Placeholder
    
    def _load_local(self, index: int, method: IrMethod):
        """Load local variable."""
        # Locals are in WRAM
        addr = self.WRAM_START + (index * 2)
        # LD HL, (addr)
        self.emitter.emit(create_instruction(0x2A))  # LD A, (HL+)
        # Simplified: load from WRAM
        # LD HL, addr
        self.emitter.emit(create_instruction(0x21, [
            addr & 0xFF,
            (addr >> 8) & 0xFF
        ]))
        # LD A, (HL)
        self.emitter.emit(create_instruction(0x7E))
        # INC HL
        self.emitter.emit(create_instruction(0x23))
        # LD H, (HL)
        self.emitter.emit(create_instruction(0x66))
        # LD L, A
        self.emitter.emit(create_instruction(0x6F))
        # PUSH HL
        self.emitter.emit(create_instruction(0xE5))
    
    def _store_local(self, index: int, method: IrMethod):
        """Store to local variable."""
        # POP HL
        self.emitter.emit(create_instruction(0xE1))
        # Store to WRAM
        addr = self.WRAM_START + (index * 2)
        # LD (addr), HL
        # LD BC, addr
        self.emitter.emit(create_instruction(0x01, [
            addr & 0xFF,
            (addr >> 8) & 0xFF
        ]))
        # LD (BC), A (simplified - need proper 16-bit store)
        # For now, placeholder
        self.emitter.emit(create_instruction(0x00))
    
    def _generate_add(self):
        """Generate addition."""
        # POP DE (second operand)
        self.emitter.emit(create_instruction(0xD1))
        # POP HL (first operand)
        self.emitter.emit(create_instruction(0xE1))
        # ADD HL, DE
        self.emitter.emit(create_instruction(0x19))
        # PUSH HL (result)
        self.emitter.emit(create_instruction(0xE5))
    
    def _generate_sub(self):
        """Generate subtraction."""
        # POP DE (second operand)
        self.emitter.emit(create_instruction(0xD1))
        # POP HL (first operand)
        self.emitter.emit(create_instruction(0xE1))
        # SUB: HL = HL - DE
        # We need to do: HL = HL - DE
        # XCHG HL, DE (swap)
        # PUSH DE
        self.emitter.emit(create_instruction(0xD5))
        # POP HL
        self.emitter.emit(create_instruction(0xE1))
        # POP DE
        self.emitter.emit(create_instruction(0xD1))
        # OR A (clear carry)
        self.emitter.emit(create_instruction(0xB7))
        # SBC HL, DE
        # LR35902 doesn't have SBC HL, so we do manual subtraction
        # LD A, L
        self.emitter.emit(create_instruction(0x7D))
        # SUB E
        self.emitter.emit(create_instruction(0x93))
        # LD L, A
        self.emitter.emit(create_instruction(0x6F))
        # LD A, H
        self.emitter.emit(create_instruction(0x7C))
        # SBC A, D
        self.emitter.emit(create_instruction(0x9A))
        # LD H, A
        self.emitter.emit(create_instruction(0x67))
        # PUSH HL
        self.emitter.emit(create_instruction(0xE5))
    
    def _generate_mul_call(self):
        """Generate call to multiplication runtime."""
        # Placeholder - would call runtime multiplication routine
        self.emitter.emit(create_instruction(0x00))
    
    def _generate_div_call(self):
        """Generate call to division runtime."""
        # Placeholder - would call runtime division routine
        self.emitter.emit(create_instruction(0x00))
    
    def _generate_call(self, method_name: str):
        """Generate method call."""
        if method_name in self.method_addresses:
            addr = self.method_addresses[method_name]
            # CALL addr
            self.emitter.emit(create_instruction(0xCD, [
                addr & 0xFF,
                (addr >> 8) & 0xFF
            ]))
        else:
            # Unknown method - placeholder
            self.emitter.emit(create_instruction(0x00))
    
    def _generate_branch(self, opcode: str, target: Any):
        """Generate branch instruction."""
        # For unconditional branch
        if opcode == 'BR' or opcode.startswith('BR_'):
            # JP target
            # For now, placeholder
            self.emitter.emit(create_instruction(0xC3, [0x00, 0x00]))
        else:
            # Conditional branch - placeholder
            self.emitter.emit(create_instruction(0x00))

