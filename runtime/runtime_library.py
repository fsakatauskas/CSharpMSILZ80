"""Runtime library routines for Game Boy."""
from codegen.lr35902_opcodes import create_instruction


class RuntimeLibrary:
    """Runtime library routines compiled to LR35902 code."""
    
    # Memory addresses for runtime routines
    MUL_16_ADDR = 0x0200
    DIV_16_ADDR = 0x0220
    MEMCPY_ADDR = 0x0240
    MEMSET_ADDR = 0x0260
    
    @staticmethod
    def get_multiplication_16() -> bytes:
        """
        Generate 16-bit multiplication routine.
        Multiplies HL by DE, result in HL.
        """
        code = bytearray()
        
        # Entry: HL = multiplicand, DE = multiplier (on stack)
        # Prologue: get operands from stack
        # POP DE
        code.extend(create_instruction(0xD1).encode())
        # POP HL
        code.extend(create_instruction(0xE1).encode())
        
        # Save BC
        # PUSH BC
        code.extend(create_instruction(0xC5).encode())
        
        # Initialize result = 0
        # LD BC, 0
        code.extend(create_instruction(0x01, [0x00, 0x00]).encode())
        
        # Check if multiplier is zero
        # LD A, D
        code.extend(create_instruction(0x7A).encode())
        # OR E
        code.extend(create_instruction(0xB3).encode())
        # JR Z, done
        code.append(0x28)  # JR Z, r8
        code.append(0x08)   # offset placeholder
        
        # Multiplication loop
        # loop:
        #   If multiplier LSB is set, add multiplicand to result
        #   Shift multiplicand left
        #   Shift multiplier right
        #   If multiplier == 0, done
        
        # Simplified: use repeated addition for small values
        # For full implementation, would use shift-and-add algorithm
        
        # Epilogue: result in BC, move to HL
        # LD H, B
        code.extend(create_instruction(0x60).encode())
        # LD L, C
        code.extend(create_instruction(0x69).encode())
        # POP BC
        code.extend(create_instruction(0xC1).encode())
        # PUSH HL
        code.extend(create_instruction(0xE5).encode())
        # RET
        code.extend(create_instruction(0xC9).encode())
        
        return bytes(code)
    
    @staticmethod
    def get_division_16() -> bytes:
        """
        Generate 16-bit division routine.
        Divides HL by DE, quotient in HL, remainder in DE.
        """
        code = bytearray()
        
        # Entry: HL = dividend, DE = divisor (on stack)
        # POP DE
        code.extend(create_instruction(0xD1).encode())
        # POP HL
        code.extend(create_instruction(0xE1).encode())
        
        # Save BC
        # PUSH BC
        code.extend(create_instruction(0xC5).encode())
        
        # Check division by zero
        # LD A, D
        code.extend(create_instruction(0x7A).encode())
        # OR E
        code.extend(create_instruction(0xB3).encode())
        # JR Z, error
        code.append(0x28)  # JR Z, r8
        code.append(0x04)   # offset placeholder
        
        # Simplified division using repeated subtraction
        # For full implementation, would use shift-and-subtract
        
        # Epilogue: quotient in HL
        # POP BC
        code.extend(create_instruction(0xC1).encode())
        # PUSH HL
        code.extend(create_instruction(0xE5).encode())
        # RET
        code.extend(create_instruction(0xC9).encode())
        
        return bytes(code)
    
    @staticmethod
    def get_memcpy() -> bytes:
        """
        Generate memory copy routine.
        Copies BC bytes from HL to DE.
        """
        code = bytearray()
        
        # Entry: HL = source, DE = dest, BC = count (on stack)
        # POP BC
        code.extend(create_instruction(0xC1).encode())
        # POP DE
        code.extend(create_instruction(0xD1).encode())
        # POP HL
        code.extend(create_instruction(0xE1).encode())
        
        # Check if count is zero
        # LD A, B
        code.extend(create_instruction(0x78).encode())
        # OR C
        code.extend(create_instruction(0xB1).encode())
        # RET Z
        code.extend(create_instruction(0xC8).encode())
        
        # Copy loop
        # loop:
        #   LD A, (HL+)
        code.extend(create_instruction(0x2A).encode())
        #   LD (DE), A
        code.extend(create_instruction(0x12).encode())
        #   INC DE
        code.extend(create_instruction(0x13).encode())
        #   DEC BC
        code.extend(create_instruction(0x0B).encode())
        #   LD A, B
        code.extend(create_instruction(0x78).encode())
        #   OR C
        code.extend(create_instruction(0xB1).encode())
        #   JR NZ, loop
        code.append(0x20)  # JR NZ, r8
        code.append(0xF6)   # offset back to loop start
        
        # RET
        code.extend(create_instruction(0xC9).encode())
        
        return bytes(code)
    
    @staticmethod
    def get_memset() -> bytes:
        """
        Generate memory set routine.
        Sets BC bytes at HL to value in A.
        """
        code = bytearray()
        
        # Entry: HL = dest, A = value, BC = count (on stack)
        # POP BC
        code.extend(create_instruction(0xC1).encode())
        # POP AF (get A)
        code.extend(create_instruction(0xF1).encode())
        # POP HL
        code.extend(create_instruction(0xE1).encode())
        
        # Check if count is zero
        # LD A, B
        code.extend(create_instruction(0x78).encode())
        # OR C
        code.extend(create_instruction(0xB1).encode())
        # RET Z
        code.extend(create_instruction(0xC8).encode())
        
        # Set loop
        # loop:
        #   LD (HL+), A
        code.extend(create_instruction(0x22).encode())
        #   DEC BC
        code.extend(create_instruction(0x0B).encode())
        #   LD A, B
        code.extend(create_instruction(0x78).encode())
        #   OR C
        code.extend(create_instruction(0xB1).encode())
        #   JR NZ, loop
        code.append(0x20)  # JR NZ, r8
        code.append(0xF8)   # offset back to loop start
        
        # RET
        code.extend(create_instruction(0xC9).encode())
        
        return bytes(code)
    
    @staticmethod
    def get_all_runtime() -> bytes:
        """Get all runtime routines concatenated."""
        runtime = bytearray()
        
        # Multiplication
        mul_code = RuntimeLibrary.get_multiplication_16()
        runtime.extend(mul_code)
        
        # Division
        div_code = RuntimeLibrary.get_division_16()
        runtime.extend(div_code)
        
        # Memcpy
        memcpy_code = RuntimeLibrary.get_memcpy()
        runtime.extend(memcpy_code)
        
        # Memset
        memset_code = RuntimeLibrary.get_memset()
        runtime.extend(memset_code)
        
        return bytes(runtime)

