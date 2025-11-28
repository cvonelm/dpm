from dpm.pkg_definition import WrapperPackageRecipe
from dpm.store import Store


class PackageRecipe(WrapperPackageRecipe):
    def __init__(self, store: Store, name):
        super().__init__(store, name, ["clang", "clang++"])
