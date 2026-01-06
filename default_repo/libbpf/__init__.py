from dpm.downloader import WebResource
from dpm.pkg_definition import BasePackageRecipe, Aspect

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [
            Needs("cc"),
            Needs("base"),
            Needs("pkg-config"),
            Needs("zstd"),
            Needs("elfutils"),
            Needs("zlib"),
        ]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_PKG_CONFIG]

    def sources(self):
        return [
            WebResource(
                self,
                "https://github.com/libbpf/libbpf/archive/refs/tags/v1.5.1.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.make(
            "",
            args=[
                "BUILD_STATIC_ONLY=y",
                f"LIBDIR={self.prefix / 'lib'}",
                f"PREFIX={self.prefix}",
            ],
            path="libbpf-1.5.1/src",
        )

    def install(self):
        self.make(
            "install",
            args=[
                "BUILD_STATIC_ONLY=y",
                f"LIBDIR={self.prefix / 'lib'}",
                f"PREFIX={self.prefix}",
            ],
            path="libbpf-1.5.1/src",
        )
