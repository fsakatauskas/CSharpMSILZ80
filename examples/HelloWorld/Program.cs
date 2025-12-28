using GameBoySDK;

namespace HelloWorld;

public static class Program
{
    // "HELLO WORLD" as tile indices (A=0, B=1, ..., space=26)
    private static readonly byte[] Message = { 
        7, 4, 11, 11, 14,   // HELLO
        26,                  // (space)
        22, 14, 17, 11, 3   // WORLD
    };
    
    public static void Main()
    {
        // Wait for VBlank before accessing VRAM
        GB.WaitVBlank();
        
        // Turn off LCD for safe VRAM access
        GB.WriteByte(GB.LCDC, 0x00);
        
        // Load font tiles into VRAM (tile 0 = 'A', tile 1 = 'B', etc.)
        GB.CopyToVRAM(GB.TILE_DATA, Font.Tiles, (ushort)Font.Tiles.Length);
        
        // Clear tile map
        for (ushort i = 0; i < 1024; i++)
        {
            GB.WriteByte((ushort)(GB.TILE_MAP + i), 26); // space tile
        }
        
        // Write "HELLO WORLD" to tile map at row 8, column 4
        ushort mapOffset = (ushort)(GB.TILE_MAP + (8 * 32) + 4);
        for (byte i = 0; i < Message.Length; i++)
        {
            GB.WriteByte((ushort)(mapOffset + i), Message[i]);
        }
        
        // Set BG palette: 11 10 01 00 = darkest to lightest
        GB.WriteByte(GB.BGP, 0xE4);
        
        // Turn on LCD with BG enabled
        GB.WriteByte(GB.LCDC, GB.LCDC_ON | GB.LCDC_BG_ON);
        
        // Infinite loop - halt to save power
        while (true)
        {
            GB.Halt();
        }
    }
}

