from dpm.downloader import Git
from dpm.pkg_definition import Aspect, BasePackageRecipe
from dpm.store import Store

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store: Store, name: str):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [
            Needs("base"),
            Needs("cc"),
            Needs("cuda"),
            Needs("cmake"),
            Needs("git"),
            Needs("scorep"),
        ]

    def aspects(self) -> list[Aspect]:
        return []

    def sources(self):
        return [
            Git(
                self,
                "https://github.com/cvonelm/scorep_plugin_nvml",
                "7ccaa6b53337989db52f7f5216fbc33f9bbb4cdb",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.store.resolve(Needs("cmake")).cmake(
            self,
            "../scorep_plugin_nvml",
            [
                "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
                f"-DCUDAToolkit_ROOT={self.store.resolve(Needs('cuda')).prefix}",
            ],
        )
        self.make()

    def install(self):
        self.make("install")
