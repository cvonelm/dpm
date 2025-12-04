from dpm.downloader import Git
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [
            Needs("base"),
            Needs("cc"),
            Needs("cmake"),
            Needs("git"),
            Needs("scorep"),
            Needs("protobuf"),
            Needs("fftw"),
        ]

    def aspects(self) -> list[Aspect]:
        return []

    def sources(self):
        return [
            Git(
                self,
                "https://github.com/score-p/scorep_plugin_metricq",
                "c1ff4d787fa6af730f4f8a151da1492618be3556",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.store.resolve(Needs("cmake")).cmake(
            self, "../scorep_plugin_metricq", ["-DCMAKE_POLICY_VERSION_MINIMUM=3.5"]
        )
        self.make()

    def install(self):
        self.make("install")
