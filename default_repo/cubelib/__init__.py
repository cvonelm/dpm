from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("cc"), Needs("base"), Needs("pkg-config"), Needs("zlib")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES]

    def sources(self):
        return [
            WebResource(
                self,
                "https://apps.fz-juelich.de/scalasca/releases/cube/4.9/dist/cubelib-4.9.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        compiler = self.store.resolve(Needs("cc"))
        toolchain = compiler.toolchain

        config_add = []
        if toolchain == "gcc":
            config_add.append("CFLAGS=-Wno-stringop-overflow")
        self.configure(
            "../cubelib-4.9/",
            [
                "--enable-static",
                "--disable-shared",
                "--with-nocross-compiler-suite=" + toolchain,
            ]
            + config_add,
        )
        self.make()

    def install(self):
        self.make("install")
