from dpm.pkg_definition import FCWrapperPackageRecipe


class PackageRecipe(FCWrapperPackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name, "oneapi", "ifx")
