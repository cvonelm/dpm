from __future__ import annotations

import json
import logging
import pathlib
import shutil
import subprocess
import uuid
from typing import TYPE_CHECKING

from dpm.downloader import Resource
from dpm.types import Forbids, Needs, Package, Provides

from .aspect import Aspect
from .environment import Environment

if TYPE_CHECKING:
    from store import Store

logger = logging.getLogger("dpm")


class BasePackageRecipe:
    def __init__(self, store: Store, name):
        self.store: Store = store
        self.name: str = name
        self.prefix: pathlib.Path = self.store.path / self.name
        self.optional_variants: set[str] = set()
        self.default_variants: set[str] = set()
        self.forbidden_variants: set[str] = set()
        self.required_variants: set[str] = set()

    def __eq__(self, other):
        return other.name == self.name

    def __hash__(self) -> int:
        return hash(
            (
                self.name,
                self.prefix,
                tuple(self.optional_variants),
                tuple(self.default_variants),
                tuple(self.forbidden_variants),
                tuple(self.required_variants),
            )
        )

    def require_variant(self, variant: str) -> bool:
        if variant in self.required_variants:
            return True
        if variant in self.forbidden_variants:
            return False
        if variant in self.optional_variants:
            self.required_variants = self.required_variants.union({variant})
            self.optional_variants = self.optional_variants.difference({variant})
            return True
        if variant in self.default_variants:
            self.required_variants = self.required_variants.union({variant})
            self.default_variants = self.default_variants.difference({variant})
            return True
        raise RuntimeError(f"Unknown variant {variant} for {self.name}!")

    def forbid_variant(self, variant: str) -> bool:
        if variant in self.required_variants:
            return False
        if variant in self.forbidden_variants:
            return True
        if variant in self.optional_variants:
            self.forbidden_variants = self.forbidden_variants.union({variant})
            self.optional_variants = self.optional_variants.intersection({variant})
            return True
        if variant in self.default_variants:
            self.forbidden_variants = self.forbidden_variants.union({variant})
            self.default_variants = self.default_variants.intersection({variant})
            return True
        raise RuntimeError(f"Unknown variant {variant} for {self.name}!")

    def provides(self) -> list[Provides]:
        return []

    def forbids(self) -> list[Forbids]:
        return []

    def needs(self) -> list[Needs]:
        return []

    def env_hook(self, env: Environment):
        # called once per registered package. For basic setup
        pass

    def env_hook_deps(self, recipe: BasePackageRecipe, env: Environment) -> None:
        # called once for every direct dependency of the registered package
        pass

    def env_hook_recursive_deps(
        self, recipe: BasePackageRecipe, env: Environment
    ) -> None:
        # called once for every dependency of the registered pacakge
        pass

    def tmpdir_execute(self, command: list[str], subdir=""):
        logger.info(
            f"Package '{self.name}': Executing {command} in {self.tmpdir / subdir}"
        )
        logger.info(f"Environment: {self.env.to_dict()}")
        ret = subprocess.run(
            command,
            check=False,
            cwd=self.tmpdir / subdir,
            env=self.env.to_dict(),
            stdout=self.log_file,
            stderr=self.log_file,
        )
        if ret.returncode != 0:
            logger.warning(
                f"Package '{self.name}': {command} failed: See {self.log_file.name}"
            )
            raise RuntimeError(str(command) + " failed!")

    def get_output(self, command: list[str]):
        return (
            subprocess.check_output(command, env=self.env.to_dict())
            .decode("utf-8")
            .strip()
        )

    def get_system_output(self, command: list[str]):
        return subprocess.check_output(command).decode("utf-8").strip()

    def configure(self, configure_srcdir: str, configure_opt: list[str], inplace=False):
        if inplace:
            self.tmpdir_execute(
                [
                    "./configure",
                    "--prefix=" + str(self.prefix),
                ],
                subdir=configure_srcdir,
            )
        else:
            self.tmpdir_execute(
                [
                    configure_srcdir + "/configure",
                    "--prefix=" + str(self.prefix),
                ]
                + configure_opt,
                subdir="build",
            )

    def make(self, target="", args: list[str] | None = None, path="build") -> None:
        make_cmd = ["make"]
        if target != "":
            make_cmd.append(target)

        make_cmd += [f"-j{str(self.env.num_processors)}"]
        if args is not None:
            make_cmd += args

        self.tmpdir_execute(make_cmd, subdir=path)

    def to_store(self) -> None:
        if self.store.is_installed(Package(self.name)):
            return
        self.required_variants = self.required_variants.union(self.default_variants)
        self.forbidden_variants = self.forbidden_variants.union(self.optional_variants)
        self.env: Environment = Environment(self.store)
        self.env.register_package(Needs(self.name))
        print(f"Installing {self.name}")

        self.tmpdir = pathlib.Path("/tmp") / ("dpm_" + str(uuid.uuid4()))
        self.tmpdir.mkdir()
        print(f"Using staging dir: {self.tmpdir}")
        self.log_file = (self.tmpdir / "build.log").open("w")
        self.builddir = pathlib.Path(self.tmpdir) / "build"
        self.builddir.mkdir()
        self.download_sources()
        print(f"Preparing sources for {self.name}")
        self.prepare()
        print(f"Building {self.name}")
        self.create()

        self.prefix.mkdir(exist_ok=True)

        try:
            print(f"Installing {self.name}")
            self.install()
            shutil.rmtree(self.tmpdir)
        except Exception:
            shutil.rmtree(self.prefix)
            raise

        self.save_spec()
        print(f"Installed {self.name}")

    def save_spec(self):
        out = {}
        out["name"] = self.name
        out["required_variants"] = list(self.required_variants)
        out["forbidden_variants"] = list(self.forbidden_variants)
        with (self.store.path / f"{self.name}.spec").open("w") as spec_file:
            json.dump(out, spec_file)

    # Defined by concrete package
    def aspects(self) -> list[Aspect]:
        raise RuntimeError("Need to define aspects!")

    @staticmethod
    def from_spec(store, name) -> BasePackageRecipe:
        with (store.path / f"{name}.spec").open("r") as spec_file:
            spec = json.load(spec_file)
            r = store.get_recipe(name)
            for v in spec["required_variants"]:
                r.require_variant(v)
            for v in spec["forbidden_variants"]:
                r.forbid_variant(v)
            return r

    def prepare(self) -> None:
        raise RuntimeError("Need to define prepare()!")

    def sources(self) -> list[Resource]:
        raise RuntimeError("Need to define sources()!")

    def install(self) -> None:
        raise RuntimeError("Need to define sources()!")

    def create(self) -> None:
        raise RuntimeError("Need to define create()!")

    def download_sources(self) -> None:
        for source in self.sources():
            source.download()

    def path(self) -> str:
        if Aspect.CONTAINS_BINARIES in self.aspects():
            return str(self.prefix / "bin")
        return ""

    def pkg_config_path(self):
        return self.prefix / "lib" / "pkgconfig"

    def which(self, binary) -> str:
        try:
            return subprocess.check_output(["which", binary]).decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Could not find {binary} in PATH!, {self.name} not installable!",
            ) from e
