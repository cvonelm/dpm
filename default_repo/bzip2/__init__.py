from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("cc"), Needs("base")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES]

    def sources(self):
        return [
            WebResource(
                self,
                "https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.make(
            "",
            args=[
                f"PREFIX={self.prefix}",
                f"CC={self.store.resolve(Needs('cc')).c_compiler_path()}",
            ],
            path="bzip2-1.0.8",
        )

    def install(self):
        self.make(
            "install",
            args=[
                f"PREFIX={self.prefix}",
                f"CC={self.store.resolve(Needs('cc')).c_compiler_path()}",
            ],
            path="bzip2-1.0.8",
        )
