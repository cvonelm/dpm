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
                "https://gitlab.com/-/project/2882658/uploads/54f6d239283bbdc75d4dbd732ced04e4/libidn2-2.3.4.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.configure(
            "../libidn2-2.3.4/",
            ["--enable-static", "--disable-shared"],
        )
        self.make()

    def install(self):
        self.make("install")
