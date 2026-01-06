from dpm.downloader import Git
from dpm.pkg_definition import Aspect, BasePackageRecipe
from dpm.store import Store

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(
        self,
        store: Store,
        name: str,
    ):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [
            Needs("cmake"),
            Needs("pkg-config"),
            Needs("git"),
            Needs("cc"),
            Needs("base"),
            Needs("otf2"),
            Needs("elfutils"),
            Needs("libbpf"),
        ]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES]

    def sources(self):
        return [
            Git(
                self,
                "https://github.com/tud-zih-energy/lo2s",
                "d0fc87307b0ca0f23531a4d9c3ae75daf65e7317",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.store.resolve(Needs("cmake")).cmake(
            self, "../lo2s", ["-Dlo2s_USE_STATIC_LIBS=ON"]
        )
        self.make()

    def install(self):
        self.make("install")
