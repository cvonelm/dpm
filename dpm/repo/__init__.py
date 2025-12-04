from __future__ import annotations

import importlib.util
import json
import logging
import pathlib
import shutil
from typing import TYPE_CHECKING

import dpm.helpers
import dpm.solver
from dpm.types import Needs, Provides

if TYPE_CHECKING:
    from dpm.pkg_definition import BasePackageRecipe

from dpm.types import Package

logger = logging.getLogger("dpm")


class Repo:
    def __init__(self, uri: str = ""):
        if uri:
            logger.info(f"Using repo {uri}")
            self.uri = pathlib.Path(uri).absolute()
        else:
            logger.info("Using default repo")
            self.uri = pathlib.Path(__file__).parent.parent.resolve() / "repo"

    def get_all_packages(self) -> list[Package]:
        return [Package(file.name, self) for file in (self.uri).iterdir()]

    def get_package_mod(self, pkg):
        logger.debug(f"Loading package module for {pkg.pkg} from {self.uri / pkg.pkg}")
        spec = importlib.util.spec_from_file_location(
            "dpm.repo." + pkg.pkg, self.uri / pkg.pkg / "__init__.py"
        )
        logger.debug(f"Spec info {spec}")
        if spec:
            package_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(package_mod)
        else:
            raise RuntimeError(f"Failed to load spec for {pkg.pkg}")
        return package_mod
