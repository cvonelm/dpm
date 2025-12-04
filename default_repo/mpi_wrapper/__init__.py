from dpm.pkg_definition import WrapperPackageRecipe

from dpm.types import Needs, Provides

import pathlib


class PackageRecipe(WrapperPackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name, ["mpicc", "mpirun", "mpicxx", "mpif90"])

    def provides(self) -> list[Provides]:
        return [Provides("mpi"), Provides("openmpi")]

    def needs(self) -> list[Needs]:
        return [Needs("cc"), Needs("fc")]

    def mpi_c_compiler_path(self) -> pathlib.Path:
        return self.prefix / "bin" / "mpicc"

    def mpi_cxx_compiler_path(self) -> pathlib.Path:
        return self.prefix / "bin" / "mpicxx"

    def mpi_fc_compiler_path(self) -> pathlib.Path:
        return self.prefix / "bin" / "mpif90"

    def mpi_vendor(self) -> str:
        # FIXME: support other mpis!
        return "openmpi"
