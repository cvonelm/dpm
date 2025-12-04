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
                "https://perftools.pages.jsc.fz-juelich.de/cicd/opari2/tags/opari2-2.0.9/opari2-2.0.9.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        compiler = self.store.resolve(Needs("cc"))
        toolchain = compiler.toolchain
        self.configure(
            "../opari2-2.0.9/",
            [
                "--enable-static",
                "--disable-shared",
                "--with-compiler-suite=" + toolchain,
            ],
        )
        self.make()

    def install(self):
        self.make("install")
