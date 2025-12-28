#!/usr/bin/env python3
"""Main entry point for MSIL to Game Boy compiler."""
import argparse
import sys
from pathlib import Path
from container import create_container
from interfaces.i_msil_reader import IMsilReader
from interfaces.i_ir_builder import IIrBuilder
from interfaces.i_code_generator import ICodeGenerator
from interfaces.i_rom_builder import IRomBuilder


def main():
    """Main compiler entry point."""
    parser = argparse.ArgumentParser(
        description='Compile .NET assemblies to Game Boy ROM files'
    )
    parser.add_argument(
        'input',
        type=str,
        help='Path to input .NET assembly (.dll file)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='output.gb',
        help='Output ROM file path (default: output.gb)'
    )
    parser.add_argument(
        '--title',
        type=str,
        default='HELLO WORLD',
        help='ROM title (max 15 characters, default: HELLO WORLD)'
    )
    parser.add_argument(
        '--cartridge-type',
        type=int,
        default=0x00,
        help='Cartridge type (default: 0x00 = ROM only)'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    if not input_path.suffix.lower() in ('.dll', '.exe'):
        print(f"Warning: Input file doesn't appear to be a .NET assembly: {input_path}", file=sys.stderr)
    
    # Create DI container
    container = create_container()
    
    # Get services
    msil_reader = container.get(IMsilReader)
    ir_builder = container.get(IIrBuilder)
    code_generator = container.get(ICodeGenerator)
    rom_builder = container.get(IRomBuilder)
    
    try:
        # Read assembly
        print(f"Reading assembly: {input_path}")
        assembly = msil_reader.read_assembly(str(input_path))
        
        # Build IR
        print("Building intermediate representation...")
        ir_module = ir_builder.build(assembly)
        print(f"  Found {len(ir_module.types)} types")
        print(f"  Found {len(ir_module.methods)} methods")
        if ir_module.entry_point:
            print(f"  Entry point: {ir_module.entry_point}")
        
        # Generate code
        print("Generating LR35902 machine code...")
        machine_code = code_generator.generate(ir_module)
        print(f"  Generated {len(machine_code)} bytes of code")
        
        # Build ROM
        print("Building ROM file...")
        rom_config = {
            'title': args.title[:15],
            'cartridge_type': args.cartridge_type,
            'rom_size': 0x00,  # 32KB
        }
        rom_data = rom_builder.build(machine_code, rom_config)
        
        # Write output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(rom_data)
        
        print(f"Success! ROM written to: {output_path}")
        print(f"  ROM size: {len(rom_data)} bytes ({len(rom_data) // 1024} KB)")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

