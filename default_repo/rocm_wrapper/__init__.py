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

    def prepare(self):
        pass

    def create(self):
        pass

    def install(self):
        rocm_path = pathlib.Path(input("ROCM PATH: "))
        self.prefix.rmdir()
        pathlib.Path(self.prefix).symlink_to(rocm_path)

    def provides(self) -> list[Provides]:
        return [Provides("rocm")]
