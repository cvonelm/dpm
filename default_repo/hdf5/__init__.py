from dpm.downloader import Git
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [
            Needs("git"),
            Needs("cc"),
            Needs("cmake"),
            Needs("mpi"),
            Needs("fc"),
            Needs("libaec"),
            Needs("base"),
        ]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES]

    def sources(self):
        return [
            Git(
                self,
                "https://github.com/HDFGroup/hdf5.git",
                "b08f2481a16b046f41c878c9d823b768f6e169f9",
            ),
        ]

    def prepare(self):
        # HDF5 is one of those CC=mpicc softwares
        self.env.env["CC"] = str(self.store.resolve(Needs("mpi")).mpi_c_compiler_path())
        self.env.env["CXX"] = str(
            self.store.resolve(Needs("mpi")).mpi_cxx_compiler_path()
        )
        self.env.env["FC"] = str(
            self.store.resolve(Needs("mpi")).mpi_fc_compiler_path()
        )

    def create(self):
        self.store.resolve(Needs("cmake")).cmake(
            self,
            "../hdf5",
            [
                "-DHDF5_BUILD_FORTRAN=ON",
                "-DHDF5_BUILD_HL_LIB=ON",
                "-DHDF5_ENABLE_PARALLEL=ON-DBUILD_STATIC_LIBS=ON",
            ],
        )
        self.make()

    def install(self):
        self.make("install")
