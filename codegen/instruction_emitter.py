"""Instruction emitter for generating LR35902 machine code."""
from typing import List, Dict
from models.gb_instruction import GBInstruction


class InstructionEmitter:
    """Emits LR35902 machine code instructions."""
    
    def __init__(self):
        self.code: List[bytes] = []
        self.labels: Dict[str, int] = {}
        self.label_refs: List[tuple] = []  # (label_name, position)
    
    def emit(self, instruction: GBInstruction) -> int:
        """Emit an instruction and return its position."""
        pos = self.get_position()
        encoded = instruction.encode()
        self.code.append(encoded)
        return pos
    
    def emit_bytes(self, data: bytes) -> int:
        """Emit raw bytes."""
        pos = self.get_position()
        self.code.append(data)
        return pos
    
    def define_label(self, name: str):
        """Define a label at current position."""
        self.labels[name] = self.get_position()
    
    def reference_label(self, name: str, position: int):
        """Reference a label (to be resolved later)."""
        self.label_refs.append((name, position))
    
    def get_position(self) -> int:
        """Get current code position."""
        return sum(len(chunk) for chunk in self.code)
    
    def resolve_labels(self) -> bytes:
        """Resolve all label references and return final code."""
        result = bytearray()
        
        for chunk in self.code:
            result.extend(chunk)
        
        # Resolve label references (for now, simple forward references)
        # In a full implementation, we'd need two-pass assembly
        for label_name, pos in self.label_refs:
            if label_name in self.labels:
                target = self.labels[label_name]
                # Calculate relative offset
                offset = target - (pos + 1)
                if -128 <= offset <= 127:
                    result[pos] = offset & 0xFF
                else:
                    raise ValueError(f"Label {label_name} too far for relative jump")
        
        return bytes(result)
    
    def get_code(self) -> bytes:
        """Get final code with labels resolved."""
        return self.resolve_labels()

