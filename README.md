# MSIL to Game Boy Compiler

A Python-based compiler that reads .NET assemblies (compiled C# DLLs), interprets MSIL bytecode, and generates Game Boy Classic ROM files targeting the Sharp LR35902 CPU.

## Features

- **MSIL Parsing**: Reads .NET assemblies using `dnfile`
- **Intermediate Representation**: Converts MSIL to an IR for code generation
- **LR35902 Code Generation**: Generates machine code for Game Boy Classic CPU
- **ROM Building**: Creates valid `.gb` ROM files with proper headers and checksums
- **Dependency Injection**: Uses `injector` library for modular, testable architecture
- **Game Boy SDK**: C# hardware abstraction layer for easy Game Boy programming

## Project Structure

```
csharp_gb_compiler/
├── main.py                 # Entry point, CLI interface
├── container.py            # Injector DI configuration
├── interfaces/             # Protocol interfaces
├── services/               # Service implementations
├── models/                 # Data models (IR, instructions, ROM header)
├── codegen/                # Code generation components
├── runtime/                # Runtime library routines
└── examples/               # Example C# projects
    ├── GameBoySDK/         # Hardware abstraction SDK
    └── HelloWorld/         # Hello World example
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install .NET SDK (for building example projects):
```bash
# Download from https://dotnet.microsoft.com/download
```

## Usage

### Compiling a C# Program

1. First, compile your C# project to a .NET assembly:
```bash
cd examples/HelloWorld
dotnet build -c Release
```

2. Then compile the assembly to a Game Boy ROM:
```bash
python main.py bin/Release/net8.0/HelloWorld.dll -o HelloWorld.gb --title "HELLO WORLD"
```

3. Test in a Game Boy emulator (e.g., [BGB](http://bgb.bircd.org/), [mGBA](https://mgba.io/)):
```bash
# Open HelloWorld.gb in your emulator
```

### Command Line Options

```
usage: main.py [-h] [-o OUTPUT] [--title TITLE] [--cartridge-type TYPE] input

positional arguments:
  input                 Path to input .NET assembly (.dll file)

optional arguments:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  Output ROM file path (default: output.gb)
  --title TITLE        ROM title (max 15 characters, default: HELLO WORLD)
  --cartridge-type TYPE
                       Cartridge type (default: 0x00 = ROM only)
```

## Supported C# Features

### Data Types
- `byte`, `sbyte` (8-bit)
- `short`, `ushort` (16-bit)
- `int`, `uint` (32-bit, software implementation)
- `bool` (8-bit)
- Arrays of primitive types
- Simple structs and classes (no inheritance)

### Language Features
- Static and instance methods
- Local variables and parameters
- Arithmetic operations (add, subtract)
- Control flow (if, while, for)
- Method calls
- Field access

### Limitations
- No garbage collection
- No inheritance or virtual methods
- No exceptions
- No generics
- Limited recursion support

## Game Boy SDK

The compiler recognizes special intrinsic methods in the `GameBoySDK.GB` class:

- `GB.WriteByte(address, value)` - Write byte to memory
- `GB.ReadByte(address)` - Read byte from memory
- `GB.CopyToVRAM(dest, src, length)` - Copy data to VRAM
- `GB.WaitVBlank()` - Wait for vertical blank
- `GB.Halt()` - Halt CPU

These are replaced with direct memory operations during compilation.

## Example: Hello World

See `examples/HelloWorld/` for a complete example that displays "HELLO WORLD" on the Game Boy screen.

The example demonstrates:
- Loading font tiles into VRAM
- Writing text to the tile map
- Configuring the LCD and palette
- Basic Game Boy graphics programming

## Architecture

The compiler uses a multi-stage pipeline:

1. **MSIL Reader**: Parses .NET PE files using `dnfile`
2. **IR Builder**: Converts MSIL instructions to intermediate representation
3. **Code Generator**: Translates IR to LR35902 machine code
4. **ROM Builder**: Assembles final ROM with headers and checksums

All components are wired together using dependency injection for modularity and testability.

## Memory Layout

```
0x0000-0x00FF: Interrupt vectors
0x0100-0x014F: Cartridge header
0x0150-0x3FFF: Code segment (~16KB)
0x4000-0x7FFF: Switchable ROM Bank
0x8000-0x9FFF: Video RAM (8KB)
0xC000-0xDFFF: Work RAM (8KB) - runtime memory
0xFF80-0xFFFE: High RAM (127 bytes)
0xFFFF: Interrupt Enable register
```

## Development

### Running Tests

```bash
# TODO: Add test suite
```

### Adding New Features

1. Define interfaces in `interfaces/`
2. Implement services in `services/`
3. Wire up dependencies in `container.py`
4. Update code generator for new MSIL opcodes

## License

[Add your license here]

## Acknowledgments

- Game Boy hardware documentation: [Pan Docs](https://gbdev.io/pandocs/)
- LR35902 CPU reference: [Game Boy CPU Manual](https://ia803208.us.archive.org/9/items/GameBoyProgManVer1.1/GameBoyProgManVer1.1.pdf)

