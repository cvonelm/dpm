from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("cc"), Needs("base"), Needs("cmake")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES, Aspect.CONTAINS_PKG_CONFIG]

    def sources(self):
        return [
            WebResource(
                self,
                "https://github.com/json-c/json-c/archive/refs/tags/json-c-0.18-20240915.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.store.resolve(Needs("cmake")).cmake(
            self,
            "../json-c-json-c-0.18-20240915",
            ["-DCMAKE_POLICY_VERSION_MINIMUM=3.5"],
        )
        self.make()

    def install(self):
        self.make("install")
