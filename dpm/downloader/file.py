import pathlib

from .resource import Resource


class File(Resource):
    def __init__(self, pkg, filename: str):
        super().__init__(pkg)
        self.filename: str = filename

    def download(self) -> None:
        res_path = self.pkg.store.repo / self.pkg.name / "misc" / self.filename

        self.pkg.tmpdir_execute(["cp", res_path, "."])
