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
            Needs("bpf_clang_cc"),
        ]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES]

    def sources(self):
        return [
            Git(
                self,
                "https://github.com/tud-zih-energy/lo2s",
                "882786142d4eb7434a50f1db15718020691c3491",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.store.resolve(Needs("cmake")).cmake(self, "../lo2s", [])
        self.make()

    def install(self):
        self.make("install")
