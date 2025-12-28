"""Dependency injection container configuration."""
from injector import Injector, Module, provider, singleton
from interfaces.i_msil_reader import IMsilReader
from interfaces.i_ir_builder import IIrBuilder
from interfaces.i_code_generator import ICodeGenerator
from interfaces.i_rom_builder import IRomBuilder
from interfaces.i_type_resolver import ITypeResolver
from services.msil_reader import MsilReader
from services.ir_builder import IrBuilder
from services.code_generator import CodeGenerator
from services.rom_builder import RomBuilder
from services.type_resolver import TypeResolver


class CompilerModule(Module):
    """DI module for compiler services."""
    
    @singleton
    @provider
    def provide_msil_reader(self) -> IMsilReader:
        """Provide MSIL reader service."""
        return MsilReader()
    
    @singleton
    @provider
    def provide_type_resolver(self) -> ITypeResolver:
        """Provide type resolver service."""
        return TypeResolver()
    
    @singleton
    @provider
    def provide_ir_builder(self, msil_reader: IMsilReader) -> IIrBuilder:
        """Provide IR builder service."""
        return IrBuilder(msil_reader)
    
    @singleton
    @provider
    def provide_code_generator(
        self,
        type_resolver: ITypeResolver
    ) -> ICodeGenerator:
        """Provide code generator service."""
        return CodeGenerator(type_resolver)
    
    @singleton
    @provider
    def provide_rom_builder(self) -> IRomBuilder:
        """Provide ROM builder service."""
        return RomBuilder()


def create_container() -> Injector:
    """Create and configure DI container."""
    return Injector([CompilerModule()])

