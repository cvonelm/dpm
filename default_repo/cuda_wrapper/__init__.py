import pathlib

from dpm.pkg_definition import Aspect, BasePackageRecipe
from dpm.types import Provides


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def sources(self):
        return []

    def aspects(self):
        return [Aspect.CONTAINS_BINARIES]

    def cuda_compiler_path(self) -> pathlib.Path:
        return self.prefix / "bin" / "nvcc"

    def prepare(self):
        pass

    def create(self):
        pass

    def install(self):
        nvcc = pathlib.Path(input("CUDA PATH: "))
        self.prefix.rmdir()
        self.prefix.symlink_to(nvcc)

    def provides(self) -> list[Provides]:
        return [Provides("cuda")]
