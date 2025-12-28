"""Game Boy LR35902 instruction models."""
from dataclasses import dataclass
from typing import Optional, List, Any


@dataclass
class GBInstruction:
    """Game Boy LR35902 instruction."""
    opcode: int
    mnemonic: str
    operands: List[Any] = None
    size: int = 1  # Instruction size in bytes
    cycles: int = 4  # CPU cycles
    
    def __post_init__(self):
        if self.operands is None:
            self.operands = []
    
    def encode(self) -> bytes:
        """Encode instruction to bytes."""
        result = bytearray([self.opcode])
        
        # Add operand bytes (little-endian for 16-bit values)
        for operand in self.operands:
            if isinstance(operand, int):
                if operand <= 0xFF:
                    result.append(operand)
                else:
                    # 16-bit value, little-endian
                    result.append(operand & 0xFF)
                    result.append((operand >> 8) & 0xFF)
            elif isinstance(operand, bytes):
                result.extend(operand)
        
        return bytes(result)

