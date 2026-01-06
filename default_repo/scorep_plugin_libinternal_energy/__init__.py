from dpm.downloader import Git
from dpm.pkg_definition import Aspect, BasePackageRecipe
from dpm.store import Store

from dpm.types import Needs


class PackageRecipe(BasePackageRecipe):
    def __init__(self, store: Store, name: str):
        super().__init__(store, name)

        self.optional_variants = {"cuda", "rocm"}

    def needs(self) -> list[Needs]:
        needs = [
            Needs("base"),
            Needs("cc"),
            Needs("cmake"),
            Needs("git"),
            Needs("scorep"),
        ]

        if "cuda" in self.required_variants:
            needs.append(Needs("cuda"))
        if "rocm" in self.required_variants:
            needs.append(Needs("rocm"))
        return needs

    def aspects(self) -> list[Aspect]:
        return []

    def sources(self):
        return [
            Git(
                self,
                "https://github.com/cvonelm/scorep_plugin_libinternal_energy",
                "324cd00f89c5c7009f93cf36c51c3e6750c5919e",
            ),
        ]

    def prepare(self):
        pass

    def create(self):
        cmake_opt = [
            "-DCMAKE_POLICY_VERSION_MINIMUM=3.5",
        ]

        if "cuda" in self.required_variants:
            cmake_opt.append("-DUSE_NVML=ON")
            cmake_opt.append(
                f"-DCUDAToolkit_ROOT={self.store.resolve(Needs('cuda')).prefix}",
            )
        else:
            cmake_opt.append("-DUSE_NVML=OFF")

        if "rocm" in self.required_variants:
            cmake_opt.append("-DUSE_ROCM_SMI=ON")
        else:
            cmake_opt.append("-DUSE_ROCM_SMI=OFF")

        self.store.resolve(Needs("cmake")).cmake(
            self, "../scorep_plugin_libinternal_energy", cmake_opt
        )
        self.make()

    def install(self):
        self.make("install")
