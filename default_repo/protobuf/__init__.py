from dpm.downloader import Git, File
from dpm.pkg_definition import Aspect, BasePackageRecipe
from dpm.store import Store

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store: Store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("tool_cc"), Needs("base"), Needs("git"), Needs("cmake")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES]

    def sources(self):
        return [
            Git(self, "https://github.com/protocolbuffers/protobuf", "v28.3"),
            File(self, "absl.patch"),
        ]

    def prepare(self):
        self.tmpdir_execute(
            ["git", "apply", f"{self.tmpdir}/absl.patch"],
            subdir="protobuf/third_party/abseil-cpp",
        )

    def create(self):
        self.store.resolve(Needs("cmake")).cmake(
            self,
            "../protobuf",
            ["-Dprotobuf_BUILD_TESTS=OFF", "-Dprotobuf_BUILD_LIBUPB=OFF"],
        )
        self.make()

    def install(self):
        self.make("install")
