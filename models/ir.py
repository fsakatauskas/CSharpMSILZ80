"""Intermediate representation models."""
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass
class IrInstruction:
    """Single IR instruction."""
    opcode: str
    operands: List[Any] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IrBasicBlock:
    """Basic block in control flow graph."""
    label: str
    instructions: List[IrInstruction] = field(default_factory=list)
    successors: List[str] = field(default_factory=list)
    predecessors: List[str] = field(default_factory=list)


@dataclass
class IrMethod:
    """Intermediate representation of a method."""
    name: str
    full_name: str
    return_type: Optional[Any] = None
    parameters: List[Any] = field(default_factory=list)
    local_variables: List[Any] = field(default_factory=list)
    basic_blocks: List[IrBasicBlock] = field(default_factory=list)
    is_static: bool = True
    is_entry_point: bool = False


@dataclass
class IrType:
    """Intermediate representation of a type."""
    name: str
    full_name: str
    size: int = 0
    fields: List[Any] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    is_struct: bool = False
    is_class: bool = False
    is_primitive: bool = False


@dataclass
class IrModule:
    """Complete intermediate representation module."""
    name: str
    types: Dict[str, IrType] = field(default_factory=dict)
    methods: Dict[str, IrMethod] = field(default_factory=dict)
    entry_point: Optional[str] = None
    constants: Dict[str, Any] = field(default_factory=dict)

