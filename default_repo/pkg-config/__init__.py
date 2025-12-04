from dpm.downloader import WebResource, Resource
from dpm.pkg_definition import Aspect, BasePackageRecipe

from dpm.types import Needs
from dpm.pkg_definition import Environment


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name)

    def needs(self) -> list[Needs]:
        return [Needs("xz"), Needs("cc"), Needs("base")]

    def aspects(self) -> list[Aspect]:
        return [Aspect.CONTAINS_BINARIES, Aspect.CONTAINS_PKG_CONFIG]

    def sources(self) -> list[Resource]:
        return [
            WebResource(
                self,
                "https://distfiles.ariadne.space/pkgconf/pkgconf-2.5.1.tar.xz",
            ),
        ]

    def prepare(self) -> None:
        pass

    def create(self) -> None:
        self.configure(
            "../pkgconf-2.5.1/",
            [
                "--enable-static",
                "--disable-shared",
            ],
        )
        self.make()

    def install(self) -> None:
        self.make("install")
        (self.prefix / "bin" / "pkg-config").symlink_to(self.prefix / "bin" / "pkgconf")

    def env_hook(self, env: Environment) -> None:
        # Instruct pkg-config to only take pkg config files from PKG_CONFIG_LIBDIR
        env.env["PKGCONFIG"] = "pkg-config --static --env-only"

    def env_hook_recursive_deps(
        self, recipe: BasePackageRecipe, env: Environment
    ) -> None:
        print(recipe.prefix)

        pkg_recipe = self.store.resolve_tree(Needs(recipe.name))
        for dep in pkg_recipe.flatten():
            if Aspect.CONTAINS_PKG_CONFIG in dep.aspects():
                pkgconfig_str = str(dep.prefix / "lib" / "pkgconfig")
                if "PKG_CONFIG_LIBDIR" not in env.env:
                    env.env["PKG_CONFIG_LIBDIR"] = pkgconfig_str
                else:
                    env.env["PKG_CONFIG_LIBDIR"] = (
                        env.env["PKG_CONFIG_LIBDIR"] + ":" + pkgconfig_str
                    )
