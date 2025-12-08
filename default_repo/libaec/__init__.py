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
                "https://gitlab.dkrz.de/-/project/117/uploads/d19a8ba56f9d578e4d8da96d01217f3e/libaec-1.1.4.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.configure(
            "../libaec-1.1.4/",
            [
                "--enable-static",
                "--disable-shared",
            ],
        )
        self.make()

    def install(self):
        self.make("install")
