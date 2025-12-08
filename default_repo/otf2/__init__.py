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
                "https://perftools.pages.jsc.fz-juelich.de/cicd/otf2/tags/otf2-3.1.1/otf2-3.1.1.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        compiler = self.store.resolve(Needs("cc"))
        self.configure(
            "../otf2-3.1.1/",
            [
                "--enable-static",
                "--disable-shared",
                "--with-nocross-compiler-suite=" + compiler.toolchain,
            ],
        )
        self.make()

    def install(self):
        self.make("install")
