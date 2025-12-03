import os

from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe
from dpm.types import Needs, Provides


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("tool_cc"), Needs("base")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES]

    def sources(self):
        return [
            WebResource(
                self,
                "https://github.com/Kitware/CMake/releases/download/v4.0.3/cmake-4.0.3.tar.gz",
            ),
        ]

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

    def prepare(self):
        pass

    def provides(self):
        return [Provides("cmake")]

    def create(self):
        compiler = self.store.resolve(Needs("tool_cc"))

        self.configure(
            "../cmake-4.0.3/",
            [
                f"LDFLAGS=-L{compiler.library_path()} -Wl,-rpath,{compiler.library_path()}",
            ],
        )
        self.make()

    def install(self):
        self.make("install")
