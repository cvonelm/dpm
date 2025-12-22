from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs

import shutil


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
                "https://github.com/openssl/openssl/releases/download/openssl-3.6.0-beta1/openssl-3.6.0-beta1.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        self.tmpdir_execute(
            [
                "./Configure",
                "no-shared",
                "--openssldir=etc/ssl",
                "--libdir=lib",
                f"--prefix={self.prefix}",
            ],
            "openssl-3.6.0-beta1",
        )
        self.make(path="openssl-3.6.0-beta1")

    def install(self):
        self.make("install", path="openssl-3.6.0-beta1")
        shutil.rmtree(self.prefix / "etc" / "ssl")
        (self.prefix / "etc" / "ssl").symlink_to("/etc/ssl")
