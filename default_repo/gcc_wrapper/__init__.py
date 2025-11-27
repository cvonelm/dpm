from dpm.pkg_definition import CCWrapperPackageRecipe


class PackageRecipe(CCWrapperPackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name, toolchain="gcc", cc="gcc", cxx="g++")
