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
                "https://archives.boost.io/release/1.88.0/source/boost_1_88_0.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.tmpdir_execute(["./bootstrap.sh"], subdir="boost_1_88_0")
        self.tmpdir_execute(
            [
                "./b2",
                "install",
                f"--prefix={self.prefix}",
                f"-j{self.env.num_processors}",
            ],
            subdir="boost_1_88_0",
        )

    def install(self):
        pass
