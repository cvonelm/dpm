from dpm.downloader import WebResource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [
            Needs("cc"),
            Needs("base"),
            Needs("openssl"),
            Needs("libidn2"),
            Needs("zlib"),
            Needs("zstd"),
            Needs("brotli"),
            Needs("libpsl"),
            Needs("libunistring"),
            Needs("pkg-config"),
            Needs("gsasl"),
            Needs("libnghttp2"),
        ]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES, Aspect.CONTAINS_PKG_CONFIG]

    def sources(self):
        return [
            WebResource(
                self,
                "https://curl.se/download/curl-8.16.0.tar.gz",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        libidn2_libs = self.get_output(["pkg-config", "libidn2", "--libs", "--static"])
        # this package is just plain allergic to correct static builds. unless it breaks,
        # dont bother with the occasional dep from somewhere else
        self.configure(
            "../curl-8.16.0/",
            [
                "--enable-static",
                "--disable-shared",
                "--with-openssl",
                f"LIBS={libidn2_libs}",
            ],
        )
        self.make()

    def install(self):
        self.make("install")
