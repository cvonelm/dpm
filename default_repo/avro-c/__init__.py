from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("cc"), Needs("base"), Needs("cmake"), Needs("jansson")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES, Aspect.CONTAINS_PKG_CONFIG]

    def sources(self):
        return [
            WebResource(
                self,
                "https://github.com/apache/avro/archive/refs/tags/release-1.12.0.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.store.resolve(Needs("cmake")).cmake(
            self, "../avro-release-1.12.0/lang/c/", []
        )
        self.make()

    def install(self):
        self.make("install")
