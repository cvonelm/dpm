from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("base"), Needs("python")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES]

    def sources(self):
        return []

    def prepare(self):
        pass

    def create(self):
        pass

    def install(self):
        self.tmpdir_execute(["python", "-m", "venv", f"{self.prefix}"])
        self.tmpdir_execute([f"{self.prefix}/bin/pip", "install", "metricq-tools"])
