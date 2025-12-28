using System;

namespace GameBoySDK;

/// <summary>
/// Game Boy hardware registers and memory-mapped I/O.
/// These are compiler intrinsics - calls are replaced with direct memory access.
/// </summary>
public static class GB
{
    // LCD Control Registers
    public const ushort LCDC = 0xFF40;  // LCD Control
    public const ushort STAT = 0xFF41;  // LCD Status
    public const ushort SCY  = 0xFF42;  // Scroll Y
    public const ushort SCX  = 0xFF43;  // Scroll X
    public const ushort LY   = 0xFF44;  // LCD Y Coordinate (read-only)
    public const ushort BGP  = 0xFF47;  // BG Palette Data
    
    // Memory regions
    public const ushort VRAM      = 0x8000;  // Video RAM start
    public const ushort TILE_DATA = 0x8000;  // Tile data (8000 method)
    public const ushort TILE_MAP  = 0x9800;  // BG Tile Map 0
    
    // LCDC flags
    public const byte LCDC_ON        = 0x80;  // LCD Display Enable
    public const byte LCDC_BG_ON     = 0x01;  // BG Display Enable
    public const byte LCDC_WIN_ON    = 0x20;  // Window Display Enable
    public const byte LCDC_OBJ_ON    = 0x02;  // OBJ (Sprite) Enable
    
    /// <summary>Write a byte to memory address</summary>
    [CompilerIntrinsic]
    public static extern void WriteByte(ushort address, byte value);
    
    /// <summary>Read a byte from memory address</summary>
    [CompilerIntrinsic]
    public static extern byte ReadByte(ushort address);
    
    /// <summary>Copy bytes to VRAM (handles VRAM access timing)</summary>
    [CompilerIntrinsic]
    public static extern void CopyToVRAM(ushort dest, byte[] src, ushort length);
    
    /// <summary>Wait for VBlank interrupt</summary>
    [CompilerIntrinsic]
    public static extern void WaitVBlank();
    
    /// <summary>Halt CPU until interrupt</summary>
    [CompilerIntrinsic]
    public static extern void Halt();
}

/// <summary>Marker attribute for compiler intrinsics</summary>
[AttributeUsage(AttributeTargets.Method)]
public class CompilerIntrinsicAttribute : Attribute { }

