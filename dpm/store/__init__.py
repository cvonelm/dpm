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


class Store:
    def __init__(self, path: str, repo: str = ""):
        self.path = pathlib.Path(path).absolute()
        if not self.path.is_dir():
            print("Store", self.path, " does not exists yet, creating")
            self.path.mkdir()

        if repo:
            logger.info(f"Using repo {repo}")
            self.repo = pathlib.Path(repo).absolute()
        else:
            logger.info("Using default repo")
            self.repo = pathlib.Path(__file__).parent.parent.resolve() / "repo"
        self._solver: dpm.solver.Solver = dpm.solver.Solver(self)

    def get_installed_packages(self) -> list[Package]:
        return [
            Package(file.name, self.repo)
            for file in self.path.iterdir()
            if file.is_dir()
        ]

    def get_all_packages(self) -> list[Package]:
        return [Package(file.name, self.repo) for file in (self.repo).iterdir()]

    def is_installed(self, pkg: Package) -> bool:
        return (self.path / pkg.pkg).is_dir()

    def stored(self):
        for pkg in self.get_installed_packages():
            r = self.get_recipe(pkg)
            if not r.required_variants and not r.forbidden_variants:
                print(f"{r.name}")
            elif r.required_variants:
                print(f"{r.name} +{r.required_variants}")
            elif r.forbidden_variants:
                print(f"{r.name} -{r.forbidden_variants}")
            else:
                print(f"{r.name} +{r.required_variants} -{r.forbidden_variants}")

    def get_package_mod(self, pkg):
        logger.debug(f"Loading package module for {pkg.pkg} from {self.repo / pkg.pkg}")
        spec = importlib.util.spec_from_file_location(
            "dpm.repo." + pkg.pkg, self.repo / pkg.pkg / "__init__.py"
        )
        logger.debug(f"Spec info {spec}")
        if spec:
            package_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(package_mod)
        else:
            raise RuntimeError(f"Failed to load spec for {pkg.pkg}")
        return package_mod

    def get_recipe(self, pkg: Package) -> BasePackageRecipe:
        if self.is_installed(pkg):
            try:
                spec_file = (self.path / f"{pkg.pkg}.spec").open("r")
                package_mod = self.get_package_mod(pkg)
                r = package_mod.PackageRecipe(self, pkg.pkg)
                spec = json.load(spec_file)
                for v in spec["required_variants"]:
                    r.require_variant(v)
                for v in spec["forbidden_variants"]:
                    r.forbid_variant(v)
                return r
            except FileNotFoundError:
                print(f"No .spec found for {pkg.pkg}, delete it?")
                if dpm.helpers.yes_no():
                    shutil.rmtree(self.path / pkg.pkg)

        package_mod = self.get_package_mod(pkg)
        return package_mod.PackageRecipe(self, pkg.pkg)

    def resolve(self, need: Needs) -> BasePackageRecipe:
        return self._solver.resolve(need)

    def resolve_tree(self, need: Needs) -> dpm.solver.PackageNode:
        return self._solver.resolve_tree(need)

    def install(self, need: Needs) -> None:
        node = self.resolve_tree(need)
        print(f"Dependency tree for Package '{need.name}'")
        node.print()
        for recipe in node.flatten():
            recipe.to_store()
            self._solver.mark_fixed(Package(recipe.name))

    def uninstall(self, provide: Provides, recursive=False) -> None:
        uninst_recipe = self._solver.resolve(provide.as_needs())

        if uninst_recipe is None:
            print(f"Can not uninstall {provide.name}: It is not installed!")
            return

        blocking = False
        for pkg in self.get_installed_packages():
            if pkg.pkg == uninst_recipe.name:
                continue
            rtree = self._solver.resolve_tree(pkg.as_needs())
            for dep in rtree.flatten():
                if dep.name == uninst_recipe.name:
                    blocking = True
                    print(f"Can not uninstall {provide.name}: {pkg.pkg} depends on it!")

        if blocking:
            print(
                f"Can not uninstall {provide.name}: Some dependent packages remaining"
            )
            return

        print(f"Removing {uninst_recipe.prefix}")
        if not dpm.helpers.yes_no():
            return
        if uninst_recipe.prefix.is_symlink():
            uninst_recipe.prefix.unlink()
        else:
            shutil.rmtree(uninst_recipe.prefix)
        pathlib.Path(str(uninst_recipe.prefix) + ".spec").unlink()
