import pathlib
import subprocess

from dpm.pkg_definition import CCWrapperPackageRecipe


class PackageRecipe(CCWrapperPackageRecipe):
    def __init__(self, store, name):
        super().__init__(store, name, toolchain="gcc", cc="gcc", cxx="g++")
        self.libs = [
            "libasan.so",
            "libcc1.so",
            "libgfortran.so.5",
            "libgomp.so.1",
            "libitm.so.1",
            "libquadmath.so.0",
            "libstdc++.so.6",
            "libubsan.so",
            "libasan.so.8",
            "libcc1.so.0",
            "libgfortran.so.5.0.0",
            "libgomp.so.1.0.0",
            "libitm.so.1.0.0",
            "libquadmath.so.0.0.0",
            "libstdc++.so.6.0.34",
            "libubsan.so.1",
            "libasan.so.8.0.0",
            "libcc1.so.0.0.0",
            "libgomp-plugin-nvptx.so",
            "libhwasan.so",
            "liblsan.so",
            "libssp.so",
            "libstdc++.so.6.0.34-gdb.py",
            "libubsan.so.1.0.0",
            "libatomic.so",
            "libgcc_s.so",
            "libgomp-plugin-nvptx.so.1",
            "libhwasan.so.0",
            "liblsan.so.0",
            "libssp.so.0",
            "libtsan.so",
            "libatomic.so.1",
            "libgcc_s.so.1",
            "libgomp-plugin-nvptx.so.1.0.0",
            "libhwasan.so.0.0.0",
            "liblsan.so.0.0.0",
            "libssp.so.0.0.0",
            "libtsan.so.2",
            "libatomic.so.1.2.0",
            "libgfortran.so",
            "libgomp.so",
            "libitm.so",
            "libquadmath.so",
            "libstdc++.so",
            "libtsan.so.2.0.0",
        ]

    def which_lib(self, lib):
        try:
            lib_path = (
                subprocess.check_output(["gcc", f"-print-file-name={lib}"])
                .decode("utf-8")
                .strip()
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Could not find {lib}!, {self.name} not installable!",
            ) from e

        lib_path = pathlib.Path(lib_path)
        if not lib_path.is_file():
            raise RuntimeError(f"Could not find {lib}!")
        else:
            return lib_path

    def library_path(self) -> pathlib.Path:
        return self.prefix / "lib"
