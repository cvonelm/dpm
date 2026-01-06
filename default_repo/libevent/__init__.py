from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe
from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [
            Needs("cc"),
            Needs("base"),
            Needs("python"),
            Needs("openssl"),
            Needs("cmake"),
        ]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES, Aspect.CONTAINS_PKG_CONFIG]

    def sources(self):
        return [
            WebResource(
                self,
                "https://github.com/libevent/libevent/releases/download/release-2.1.12-stable/libevent-2.1.12-stable.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.store.resolve(Needs("cmake")).cmake(self, "../libevent-2.1.12-stable/", [])
        self.make()

    def install(self):
        self.make("install")
