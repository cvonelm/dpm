from __future__ import annotations

from dpm.types import Needs, Provides, Forbids, Package, PackageNode, NeedsNode
from dpm.helpers import select_helper

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dpm.pkg_definition import BasePackageRecipe
    from dpm.store import Store

import logging

logger = logging.getLogger("dpm")


class Solver:
    def __init__(self, store: Store):
        self.store: Store = store

        # list of concrete providing packages for every provides class
        self.providers: dict[Provides, list[Package]] = {}

        self.recipes: dict[Package, BasePackageRecipe] = {}

        # fill this dict with a mapping for the reasons why a provider cant
        # be installed for debugging reasons
        self.forbid_reason: dict[Provides, str] = {}

        self.fixed: list[Provides] = []

        # Fill providers from all available recipes
        for pkg in self.store.get_all_packages():
            recipe: BasePackageRecipe = self.store.get_recipe(pkg)
            self.recipes[pkg] = recipe

            # Every pkg provides itself
            self.providers[pkg.as_provides()] = [pkg]

            for provide in recipe.provides():
                if provide not in self.providers:
                    self.providers[provide] = [pkg]
                else:
                    self.providers[provide].append(pkg)

        for pkg in self.store.get_installed_packages():
            self.mark_fixed(pkg)

    def set_forbid_reason(self, pkg: Provides, reason: str):
        if pkg in self.forbid_reason:
            return
        self.forbid_reason[pkg] = reason

    def print_reason(self, name: Provides):
        print(f"Can not install {name.name}: {self.forbid_reason[name]}")

    def candidate_exists(self, candidate: Provides) -> bool:
        return len(self.providers[candidate]) != 0

    def recurse_forbid(self, forbids: Forbids):
        logger.info(f"Forbidding {forbids.name}")

        # Forbid every package that provides forbids
        if Provides(forbids.name) in self.providers:
            for pkg in self.providers[Provides(forbids.name)]:
                if pkg.pkg != forbids.name:
                    self.recurse_forbid(Forbids(pkg.pkg))

        # Forbid also every package that depends on forbids
        for pkg, recipe in self.recipes.items():
            if Needs(forbids.name) in recipe.needs():
                self.set_forbid_reason(
                    pkg.as_provides(),
                    f"{pkg.pkg} depends on {forbids.name} and it is forbidden",
                )
                logger.info(f"{self.forbid_reason[pkg.as_provides()]}")
                self.recurse_forbid(Forbids(pkg.pkg))

        # Remove the forbidden Provides from every other provide class
        mark_delete: list[Provides] = []

        for provide, provides in self.providers.items():
            prev_length: int = len(self.providers[provide])

            self.providers[provide] = [
                candidate
                for candidate in provides
                if candidate != Package(forbids.name, self.store.repo)
            ]

            # Mark provide class as delete if it is now empty
            if prev_length != 0 and len(self.providers[provide]) == 0:
                self.set_forbid_reason(
                    provide,
                    f"No provider for {provide.name} left (Last option was: {forbids.name})!",
                )
                mark_delete.append(provide)

        for delete in mark_delete:
            self.recurse_forbid(Forbids(delete.name))

    def mark_fixed(self, pkg: Package) -> None:
        logger.info(f"Marking {pkg.pkg} as fixed")

        # We never delete self.provides[provide.name], so if there is
        # no element for need.name in self.providers, then we have never
        # seen a package that provides need.name, which is an error
        if pkg not in self.recipes:
            raise RuntimeError(f"{pkg.pkg} is not build by any recipe!!")

        recipe: BasePackageRecipe = self.recipes[pkg]

        # For every provide, of the mark_fixed pkg, only allow it.
        for provide in recipe.provides():
            others = [
                provider for provider in self.providers[provide] if provider != pkg
            ]
            for other in others:
                self.set_forbid_reason(
                    other.as_provides(),
                    f"Provides('{provide.name}') is already satisfied through {pkg.pkg}",
                )
                logger.info(self.forbid_reason[other.as_provides()])

                self.recurse_forbid(Forbids(other.pkg))

            self.providers[provide] = [pkg]

            self.fixed.append(provide)

        for forbid in recipe.forbids():
            self.set_forbid_reason(
                Provides(forbid.name), f"Package({pkg.pkg}') forbids {forbid.name}"
            )
            logger.info(self.forbid_reason[Provides(forbid.name)])
            self.recurse_forbid(forbid)

        self.fixed.append(Provides(pkg.pkg))

    def get_variant_satisfying_providers(self, need: Needs) -> list[Package]:
        filtered_providers: list[Package] = []
        for provider in self.providers[need.as_provides()]:
            filtered = False
            for variant in need.required_variants:
                # Do not use provider for need.name if the variant we require is forbidden by it
                if not self.recipes[provider].require_variant(variant):
                    if Provides(provider.pkg) in self.fixed:
                        raise RuntimeError(
                            f"{provider.pkg} is required, but the {variant} is forbidden by it!"
                        )

                    self.set_forbid_reason(
                        Provides(provider.pkg),
                        f"{need.name} requires variant '{variant}', but {provider.pkg} forbids it",
                    )
                    break
            else:
                filtered = True

            for variant in need.forbidden_variants:
                # Do not use provider for need.name if the variant we require is forbidden by it
                if not self.recipes[provider].forbid_variant(variant):
                    if provider in self.fixed:
                        raise RuntimeError(
                            f"{provider.pkg} is forbidden, but the {variant} is required by it!"
                        )

                    self.set_forbid_reason(
                        Provides(provider.pkg),
                        f"{need.name} forbids variant '{variant}', but {provider.pkg} requires it",
                    )
                    break
            else:
                filtered = True
            if filtered:
                filtered_providers.append(provider)
        return filtered_providers

    # Two-step solving process for Needs("some_pkg")
    # First solve recursively the requirements for need, ignoring Names for which
    # there are multiple providers
    #
    # After that, ask the user what pkg they want to select if there are multiple providers
    # and resolve
    def solve(self, need: Needs, parent=None) -> NeedsNode:
        """Solve the requirements of the package need recursively, skipping over names for which multiple providers exist

        Arguments:
        needs -- Needs Object specifying the required package
        processed -- Recursively filled list with the packages we have already processed
        """
        logger.info(f"Solving {need.name}")

        # We never delete self.provides[provide.name], so if there is
        # no element for need.name in self.providers, then we have never
        # seen a package that provides need.name, which is an error
        if need.as_provides() not in self.providers:
            raise RuntimeError(f"{need.name} is provided by no package!")

        # filter the list of all providers for the need
        # for those that can satisfy the variant requirements of need
        filtered_providers = self.get_variant_satisfying_providers(need)

        if len(filtered_providers) == 0:
            raise RuntimeError(f"No provider for {need.name} left!")

        self.providers[need.as_provides()] = filtered_providers

        # self.provide now only contains providers for the `need` that satisfy its variant requirements

        child = None
        if parent is None:
            parent = NeedsNode(need)
            child = parent
        else:
            parent.children.append(NeedsNode(need))
            child = parent.children[-1]

        selected = self.solved(need.as_provides())
        if selected is not None:
            for child_need in self.recipes[selected].needs():
                self.solve(child_need, child)
            self.mark_fixed(selected)

        return parent

    def solved(self, provide: Provides):
        if len(self.providers[provide]) == 1:
            return self.providers[provide][0]
        return None

    def resolve_options(self, node: NeedsNode, package_node=None) -> PackageNode:
        package_child: PackageNode | None = None

        pkg = self.solved(Provides(node.needs.name))

        if pkg is not None:
            recipe = self.recipes[pkg]

            if package_node is None:
                package_node = PackageNode(recipe)
                package_child = package_node
            else:
                package_node.children.append(PackageNode(recipe))
                package_child = package_node.children[-1]

        else:
            num = select_helper(
                f"Select a provider for {node.needs.name}",
                [pkg.pkg for pkg in self.providers[node.needs.as_provides()]],
            )

            node = self.solve(Needs(self.providers[node.needs.as_provides()][num].pkg))
            package_node = self.resolve_options(node, package_node)

        for need_child in node.children:
            self.resolve_options(need_child, package_child)

        return package_node

    def resolve_tree(self, pkg: Needs) -> PackageNode:
        node: NeedsNode = self.solve(pkg)
        return self.resolve_options(node)

    def resolve(self, need: Needs) -> BasePackageRecipe:
        if need.as_provides() in self.fixed:
            pkg = self.solved(need.as_provides())
            return self.recipes[pkg]
