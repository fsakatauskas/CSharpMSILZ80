"""Game Boy ROM header structure."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RomHeader:
    """Game Boy cartridge header."""
    # Nintendo logo (0x0104-0x0133) - required for boot
    nintendo_logo: bytes = None
    
    # Title (0x0134-0x0143) - max 16 characters
    title: str = "HELLO WORLD"
    
    # Manufacturer code (0x013F-0x0142)
    manufacturer_code: bytes = b'\x00\x00\x00'
    
    # CGB flag (0x0143)
    cgb_flag: int = 0x00  # 0x80 = CGB, 0xC0 = CGB+DMG
    
    # New licensee code (0x0144-0x0145)
    new_licensee_code: bytes = b'\x00\x00'
    
    # SGB flag (0x0146)
    sgb_flag: int = 0x00  # 0x03 = SGB
    
    # Cartridge type (0x0147)
    cartridge_type: int = 0x00  # 0x00 = ROM only
    
    # ROM size (0x0148)
    rom_size: int = 0x00  # 0x00 = 32KB (no banking)
    
    # RAM size (0x0149)
    ram_size: int = 0x00  # 0x00 = No RAM
    
    # Destination code (0x014A)
    destination_code: int = 0x00  # 0x00 = Japan, 0x01 = Other
    
    # Old licensee code (0x014B)
    old_licensee_code: int = 0x00
    
    # Mask ROM version (0x014C)
    mask_rom_version: int = 0x00
    
    # Header checksum (0x014D)
    header_checksum: int = 0x00
    
    # Global checksum (0x014E-0x014F)
    global_checksum: int = 0x0000
    
    def __post_init__(self):
        """Initialize default Nintendo logo if not provided."""
        if self.nintendo_logo is None:
            # Standard Nintendo logo bytes (required for boot)
            self.nintendo_logo = bytes([
                0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B,
                0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
                0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
                0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
                0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC,
                0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E
            ])

