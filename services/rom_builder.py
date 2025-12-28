"""ROM builder service for creating valid Game Boy ROM files."""
from typing import Dict, Any
from interfaces.i_rom_builder import IRomBuilder
from models.rom_header import RomHeader
from runtime.runtime_library import RuntimeLibrary


class RomBuilder(IRomBuilder):
    """Builds valid Game Boy ROM files with headers and checksums."""
    
    # ROM layout
    HEADER_START = 0x0100
    HEADER_SIZE = 0x50
    CODE_START = 0x0150
    MIN_ROM_SIZE = 32 * 1024  # 32KB minimum
    
    def build(self, code: bytes, config: Dict[str, Any]) -> bytes:
        """
        Build a valid .gb ROM file with header and checksums.
        
        Args:
            code: Generated machine code
            config: ROM configuration (title, cartridge type, etc.)
            
        Returns:
            Complete ROM file bytes
        """
        # Create header
        title = config.get('title', 'HELLO WORLD')
        print(f"  ROM title: {title}")
        
        header = RomHeader(
            title=title,
            cartridge_type=config.get('cartridge_type', 0x00),
            rom_size=config.get('rom_size', 0x00),
        )
        
        # Don't add runtime for complete programs (like Hello World)
        # The code generator already includes everything needed
        skip_runtime = config.get('skip_runtime', True)
        
        if skip_runtime:
            final_code = code
        else:
            final_code = self._add_runtime(code)
        
        # Calculate ROM size (pad to minimum 32KB)
        rom_size = max(self.MIN_ROM_SIZE, self._round_up_to_power_of_2(len(final_code) + self.CODE_START))
        
        # Build ROM
        rom = bytearray(rom_size)
        
        # Fill with 0xFF (unused ROM space)
        for i in range(len(rom)):
            rom[i] = 0xFF
        
        # Write interrupt vectors (0x0000-0x00FF)
        # RST 00H jumps to 0x0100
        rom[0x0000] = 0x00  # NOP
        rom[0x0001] = 0xC3  # JP
        rom[0x0002] = 0x00
        rom[0x0003] = 0x01  # JP to 0x0100
        
        # Write cartridge header (0x0100-0x014F)
        self._write_header(rom, header)
        
        # Write code (starting at 0x0150)
        code_start = self.CODE_START
        rom[code_start:code_start + len(final_code)] = final_code
        
        # Calculate and write checksums
        self._write_checksums(rom, header)
        
        return bytes(rom)
    
    def _add_runtime(self, code: bytes) -> bytes:
        """Add runtime library to code."""
        runtime = RuntimeLibrary.get_all_runtime()
        # Runtime goes before user code
        return runtime + code
    
    def _write_header(self, rom: bytearray, header: RomHeader):
        """Write cartridge header to ROM."""
        # Entry point (0x0100-0x0103)
        rom[0x0100] = 0x00  # NOP
        rom[0x0101] = 0xC3  # JP
        rom[0x0102] = 0x50  # Low byte of jump target
        rom[0x0103] = 0x01  # High byte of jump target (0x0150)
        
        # Nintendo logo (0x0104-0x0133)
        logo = header.nintendo_logo
        rom[0x0104:0x0104 + len(logo)] = logo
        
        # Title (0x0134-0x0143) - max 16 characters, padded with 0x00
        title_bytes = header.title.upper().encode('ascii', errors='ignore')[:16]
        # Clear title area first
        for i in range(0x0134, 0x0144):
            rom[i] = 0x00
        rom[0x0134:0x0134 + len(title_bytes)] = title_bytes
        
        # CGB flag (0x0143)
        rom[0x0143] = header.cgb_flag
        
        # New licensee code (0x0144-0x0145)
        rom[0x0144:0x0146] = header.new_licensee_code[:2]
        
        # SGB flag (0x0146)
        rom[0x0146] = header.sgb_flag
        
        # Cartridge type (0x0147)
        rom[0x0147] = header.cartridge_type
        
        # ROM size (0x0148)
        rom[0x0148] = header.rom_size
        
        # RAM size (0x0149)
        rom[0x0149] = header.ram_size
        
        # Destination code (0x014A)
        rom[0x014A] = header.destination_code
        
        # Old licensee code (0x014B)
        rom[0x014B] = header.old_licensee_code
        
        # Mask ROM version (0x014C)
        rom[0x014C] = header.mask_rom_version
    
    def _write_checksums(self, rom: bytearray, header: RomHeader):
        """Calculate and write header and global checksums."""
        # Header checksum (0x014D)
        # x = 0; for i in 0x0134..0x014C: x = x - mem[i] - 1
        checksum = 0
        for i in range(0x0134, 0x014D):
            checksum = checksum - rom[i] - 1
        checksum &= 0xFF
        rom[0x014D] = checksum
        
        # Global checksum (0x014E-0x014F)
        # Sum of all bytes except 0x014E-0x014F
        global_sum = 0
        for i in range(len(rom)):
            if i not in (0x014E, 0x014F):
                global_sum += rom[i]
        global_sum &= 0xFFFF
        rom[0x014E] = global_sum & 0xFF
        rom[0x014F] = (global_sum >> 8) & 0xFF
    
    def _round_up_to_power_of_2(self, n: int) -> int:
        """Round up to next power of 2."""
        if n <= 0:
            return 1
        n -= 1
        n |= n >> 1
        n |= n >> 2
        n |= n >> 4
        n |= n >> 8
        n |= n >> 16
        return n + 1

