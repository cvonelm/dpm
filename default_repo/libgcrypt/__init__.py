from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe


from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("cc"), Needs("base"), Needs("libgpg-error")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES, Aspect.CONTAINS_PKG_CONFIG]

    def sources(self):
        return [
            WebResource(
                self,
                "https://www.gnupg.org/ftp/gcrypt/libgcrypt/libgcrypt-1.11.2.tar.bz2",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.configure(
            "../libgcrypt-1.11.2/",
            ["--enable-static", "--disable-shared"],
        )
        self.make()

    def install(self):
        self.make("install")
