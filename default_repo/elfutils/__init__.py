from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Forbids, Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [
            Needs("cc"),
            Needs("base"),
            Needs("bzip2"),
            Needs("xz"),
            Needs("zstd"),
            Needs("zlib"),
            Needs("pkg-config"),
        ]

    def forbids(self) -> list[Forbids]:
        return [Forbids("intel_cc")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES, Aspect.CONTAINS_PKG_CONFIG]

    def sources(self):
        return [
            WebResource(
                self,
                "https://sourceware.org/elfutils/ftp/0.193/elfutils-0.193.tar.bz2",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        # this package is just plain allergic to correct static builds. unless it breaks,
        # dont bother with the occasional dep from somewhere else
        self.configure("../elfutils-0.193/", [])
        self.make()

    def install(self):
        self.make("install")
