from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dpm.pkg_definition import BasePackageRecipe


class Provides:
    def __init__(self, name: str):
        self.name: str = name

    def __eq__(self, other) -> bool:
        if not isinstance(other, Provides):
            raise RuntimeError(
                f"comparing Provides object to object of type {type(other)}!"
            )
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return f"Provides: {self.name}"

    def as_needs(self) -> Needs:
        return Needs(self.name)


class Needs:
    def __init__(self, name: str, required_variants=None, forbidden_variants=None):
        self.name: str = name
        if required_variants is None:
            self.required_variants = set()
        else:
            self.required_variants = required_variants
        if forbidden_variants is None:
            self.forbidden_variants = set()
        else:
            self.forbidden_variants = forbidden_variants

    def __hash__(self):
        return hash(
            (self.name, tuple(self.required_variants), tuple(self.forbidden_variants))
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Needs):
            raise RuntimeError(
                f"comparing Needs object to object of type {type(other)}!"
            )
        return (
            self.name == other.name
            and self.required_variants == self.required_variants
            and self.forbidden_variants == self.forbidden_variants
        )

    def as_provides(self) -> "Provides":
        return Provides(self.name)


# Forbids("lo2s") forbids any lo2s
class Forbids:
    def __init__(self, name: str):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        if not isinstance(other, Forbids):
            raise RuntimeError(f"comparing Provides to object of type {type(other)}!")
        return self.name == other.name


class NeedsNode:
    def __init__(self, needs: Needs):
        self.needs: Needs = needs
        self.children: list[NeedsNode] = []

    def contains(self, needs: Needs) -> bool:
        res: bool = needs == self.needs.name
        for child in self.children:
            res = res | child.contains(needs)
        return res

    def print(self, level=0):
        print("\t" * level + self.needs.name)
        for child in self.children:
            child.print(level + 1)

    def flatten(self):
        s = {}
        for child in self.children:
            s = s | child.flatten()
        return s | dict.fromkeys([self.needs])


class PackageNode:
    def __init__(self, pkg: BasePackageRecipe):
        self.pkg: BasePackageRecipe = pkg
        self.children: list[PackageNode] = []

    def contains(self, pkg: BasePackageRecipe) -> bool:
        res: bool = pkg.name == self.pkg.name
        for child in self.children:
            res = res | child.contains(pkg)
        return res

    def print(self, level=0) -> None:
        print("\t" * level + self.pkg.name)
        for child in self.children:
            child.print(level + 1)

    def flatten(self):
        s = {}
        for child in self.children:
            s = s | child.flatten()
        return s | dict.fromkeys([self.pkg])


class Package:
    def __init__(self, pkg: str, repo: Path = Path()):
        self.pkg = pkg
        self.repo = repo

    def __eq__(self, other) -> bool:
        if not isinstance(other, Package):
            raise RuntimeError(
                f"comparing Package object to object of type {type(other)}!"
            )
        return self.pkg == other.pkg

    def as_needs(self) -> Needs:
        return Needs(self.pkg)

    def __hash__(self):
        return hash(self.pkg)

    def as_provides(self) -> "Provides":
        return Provides(self.pkg)
