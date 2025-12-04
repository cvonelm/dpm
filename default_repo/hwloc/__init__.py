from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("cc"), Needs("base")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES, Aspect.CONTAINS_PKG_CONFIG]

    def sources(self):
        return [
            WebResource(
                self,
                "https://download.open-mpi.org/release/hwloc/v2.12/hwloc-2.12.1.tar.gz",
            ),
        ]

    def prepare(self) -> None:
        pass

    def create(self) -> None:
        self.configure(
            "../hwloc-2.12.1/",
            [
                "--disable-nvml",  # Those things only lead to hurt, because they are never correctly found
                "--disable-cuda",
            ],
        )
        self.make()

    def install(self) -> None:
        self.make("install")
