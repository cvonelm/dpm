from dpm.pkg_definition import WrapperPackageRecipe

from dpm.types import Provides, Needs


class PackageRecipe(WrapperPackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name, ["cmake"])

    def provides(self) -> list[Provides]:
        return [Provides("cmake")]

    def cmake(self, pkg, cmake_srcdir: str, cmake_opt: list[str]):
        if "CC" in pkg.env.env:
            cmake_opt.append("-DCMAKE_C_COMPILER=" + pkg.env.env["CC"])
            cmake_opt.append("-DCMAKE_CXX_COMPILER=" + pkg.env.env["CXX"])
        if "FC" in pkg.env.env:
            cmake_opt.append("-DCMAKE_Fortran_COMPILER=" + pkg.env.env["FC"])

        cmake_opt.append("-DCMAKE_POSITION_INDEPENDENT_CODE=ON")
        cmake_opt.append("-DBUILD_SHARED_LIBS=OFF")

        pkg_tree = self.store.resolve_tree(Needs(pkg.name))

        PREFIX_PATH = [str(dep.prefix) for dep in pkg_tree.flatten()]

        cmake_prefix_path = ";".join(PREFIX_PATH)
        cmake_opt.append("-DCMAKE_PREFIX_PATH=" + cmake_prefix_path)

        cmake_opt.append("-DCMAKE_INSTALL_PREFIX=" + str(pkg.prefix))
        pkg.tmpdir_execute(["cmake", cmake_srcdir] + cmake_opt, subdir="build")
