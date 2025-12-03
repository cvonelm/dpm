import pathlib

from dpm.types import Provides

from .wrapper_recipe import WrapperPackageRecipe


class CCWrapperPackageRecipe(WrapperPackageRecipe):
    def __init__(self, store, name: str, toolchain: str, cc, cxx):
        super().__init__(store, name, [cc, cxx])
        self.toolchain = toolchain
        self.cc = cc
        self.cxx = cxx

    def c_compiler_path(self) -> pathlib.Path:
        return self.prefix / "bin" / self.cc

    def cxx_compiler_path(self) -> pathlib.Path:
        return self.prefix / "bin" / self.cxx

    def library_path(self) -> pathlib.Path:
        raise RuntimeError("Need to define compiler libraries!")

    def env_hook(self, env):
        env.env["CC"] = str(self.c_compiler_path())
        env.env["CXX"] = str(self.cxx_compiler_path())

    def provides(self) -> list[Provides]:
        return [Provides("cc"), Provides(self.toolchain + "_cc")]
