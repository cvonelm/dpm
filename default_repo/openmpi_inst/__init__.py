from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

import pathlib
from dpm.types import Needs, Provides


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [
            Needs("cc"),
            Needs("base"),
            Needs("hwloc"),
            Needs("zlib"),
            Needs("pmix"),
        ]

    def provides(self) -> list[Provides]:
        return [Provides("mpi"), Provides("openmpi")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES, Aspect.CONTAINS_PKG_CONFIG]

    def sources(self):
        return [
            WebResource(
                self,
                "https://download.open-mpi.org/release/open-mpi/v5.0/openmpi-5.0.8.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.configure(
            "../openmpi-5.0.8/",
            [],
        )
        self.make()

    def install(self):
        self.make("install")

    def mpi_c_compiler_path(self) -> pathlib.Path:
        return self.prefix / "bin" / "mpicc"

    def mpi_cxx_compiler_path(self) -> pathlib.Path:
        return self.prefix / "bin" / "mpicxx"

    def mpi_fc_compiler_path(self) -> pathlib.Path:
        return self.prefix / "bin" / "mpif90"

    def mpi_vendor(self) -> str:
        # FIXME: support other mpis!
        return "openmpi"
