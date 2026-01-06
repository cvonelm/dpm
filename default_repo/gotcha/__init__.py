from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("cc"), Needs("base"), Needs("cmake")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES]

    def sources(self):
        return [
            WebResource(
                self,
                "https://github.com/LLNL/GOTCHA/archive/refs/tags/1.0.8.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.store.resolve(Needs("cmake")).cmake(
            self, "../GOTCHA-1.0.8/", ["-DCMAKE_POLICY_VERSION_MINIMUM=3.5"]
        )
        self.make()

    def install(self):
        self.make("install")
