from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dpm.store import Store
    from dpm.types import Needs


class Environment:
    def __init__(self, store: Store):
        self.store = store
        self.env = {}
        self.PATH = []
        self.env["HOME"] = os.environ["HOME"]
        self.num_processors = int(
            subprocess.run(
                "nproc", check=False, text=True, stdout=subprocess.PIPE
            ).stdout,
        )

    def register_package(self, need: Needs):
        pkg_recipe = self.store.resolve_tree(need)
        pkg_recipe.pkg.env_hook(self)
        self.PATH.append(str((pkg_recipe.pkg.prefix / "bin").absolute()))
        for dep in pkg_recipe.children:
            self.PATH.append(str((dep.pkg.prefix / "bin").absolute()))
            dep.pkg.env_hook(self)
            dep.pkg.env_hook_deps(dep.pkg, self)
        for dep in pkg_recipe.flatten():
            dep.env_hook(self)
            dep.env_hook_recursive_deps(pkg_recipe.pkg, self)

    def to_dict(self) -> dict[str, str]:
        res = self.env

        res["PATH"] = ":".join(self.PATH)
        return self.env
