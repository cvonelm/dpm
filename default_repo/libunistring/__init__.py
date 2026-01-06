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
                "http://www.gnu.ftp.uni-erlangen.de/gnu/libunistring/libunistring-1.3.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.configure(
            "../libunistring-1.3/",
            ["--enable-static", "--disable-shared"],
        )
        self.make()

    def install(self):
        self.make("install")
