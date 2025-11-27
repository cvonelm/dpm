from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs, Provides


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)
        self.optional_variants = {"cuda"}

    def needs(self) -> list[Needs]:
        needs = [
            Needs("cc"),
            Needs("fc"),
            Needs("mpi"),
            Needs("pkg-config"),
            Needs("base"),
            Needs("cubelib"),
            Needs("otf2"),
            Needs("cubew"),
            Needs("opari2"),
            Needs("gotcha"),
        ]

        if "cuda" in self.required_variants:
            needs.append(Needs("cuda"))
        return needs

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES]

    def Provides(self) -> list[Provides]:
        return [Provides("scorep_cc"), Provides("scorep_fc"), Provides("scorep_mpi")]

    def sources(self):
        return [
            WebResource(
                self,
                "https://perftools.pages.jsc.fz-juelich.de/cicd/scorep/tags/scorep-9.1/scorep-9.1.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        compiler = self.store.resolve(Needs("cc"))
        fortran = self.store.resolve(Needs("fc"))
        mpi = self.store.resolve(Needs("mpi"))

        configure_opt = [
            "--enable-static",
            "--disable-shared",
            f"--with-libgotcha={str(self.store.resolve(Needs('gotcha')).prefix)}",
            "--with-nocross-compiler-suite=" + compiler.toolchain,
            "--with-mpi=" + mpi.mpi_vendor(),
            f"CC={str(compiler.c_compiler_path())}",
            f"CXX={str(compiler.cxx_compiler_path())}",
            f"FC={str(fortran.fc_compiler_path())}",
            f"MPICC={mpi.mpi_c_compiler_path()}",
            f"MPICXX={mpi.mpi_cxx_compiler_path()}",
            f"MPIFC={mpi.mpi_fc_compiler_path()}",
            f"MPIF77={mpi.mpi_fc_compiler_path()}",
        ]

        if "cuda" in self.required_variants:
            cuda = self.store.resolve(Needs("cuda"))
            configure_opt = configure_opt + [
                f"NVCC={cuda.cuda_compiler_path()}",
                "--enable-cuda",
                f"--with-libcudart={cuda.prefix}",
            ]
        self.configure(
            "../scorep-9.1/",
            configure_opt,
        )
        self.make()

    def install(self):
        self.make("install")
