"""Register allocation strategy for LR35902."""
from typing import Dict, Optional, List
from enum import Enum


class Register(Enum):
    """LR35902 registers."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    H = "H"
    L = "L"
    BC = "BC"
    DE = "DE"
    HL = "HL"
    SP = "SP"
    AF = "AF"


class RegisterAllocator:
    """Manages register allocation for code generation."""
    
    def __init__(self):
        # Register usage tracking
        self.allocated: Dict[str, Register] = {}
        self.free_registers = [
            Register.BC,
            Register.DE,
            Register.HL,
        ]
        self.spill_offset = 0  # Offset in stack frame for spilled variables
    
    def allocate(self, var_name: str) -> Register:
        """Allocate a register for a variable."""
        if var_name in self.allocated:
            return self.allocated[var_name]
        
        if self.free_registers:
            reg = self.free_registers.pop(0)
            self.allocated[var_name] = reg
            return reg
        
        # No free registers - spill to stack
        # For now, return HL as default (caller must handle spilling)
        return Register.HL
    
    def free(self, var_name: str):
        """Free a register."""
        if var_name in self.allocated:
            reg = self.allocated[var_name]
            if reg not in self.free_registers:
                self.free_registers.append(reg)
            del self.allocated[var_name]
    
    def get_register(self, var_name: str) -> Optional[Register]:
        """Get register for variable if allocated."""
        return self.allocated.get(var_name)
    
    def reset(self):
        """Reset allocator state."""
        self.allocated.clear()
        self.free_registers = [Register.BC, Register.DE, Register.HL]
        self.spill_offset = 0

