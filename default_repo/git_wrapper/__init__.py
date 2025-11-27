from dpm.pkg_definition import WrapperPackageRecipe

from dpm.types import Provides


class PackageRecipe(WrapperPackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name, ["git"])

    def provides(self) -> list[Provides]:
        return [Provides("git")]
