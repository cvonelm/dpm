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
            Needs("hwloc"),
            Needs("python"),
            Needs("libevent"),
        ]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES, Aspect.CONTAINS_PKG_CONFIG]

    def sources(self):
        return [
            WebResource(
                self,
                "https://github.com/openpmix/openpmix/releases/download/v4.1.1/pmix-4.1.1.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.configure(
            "../pmix-4.1.1/",
            [
                f"--with-libevent={self.store.resolve(Needs('libevent')).prefix}",
                f"--with-hwloc={self.store.resolve(Needs('hwloc')).prefix}",
            ],
        )
        self.make()

    def install(self):
        self.make("install")
