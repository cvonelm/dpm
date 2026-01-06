from dpm.pkg_definition import CCWrapperPackageRecipe


class PackageRecipe(CCWrapperPackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name, toolchain="clang", cc="clang", cxx="clang++")
