"""Expand Solidity import statements for Etherscan verification service.

Mainly need for EtherScan verification service.
"""
import os
from typing import Tuple

from populus import Project


class Expander:
    """Solidity import expanded."""

    def __init__(self, project: Project):
        self.project = project
        self.processed_imports = set()
        self.pragma_processed = False

    def expand_file(self, import_path: str, parent_path=None):
        """Read Solidity source code and expart any import paths inside.

        Supports Populus remapping settings:

        http://populus.readthedocs.io/en/latest/config.html#compiler-settings

        :param import_path:
        """

        # TODO: properly handle import remapping here, read them from project config
        if import_path.startswith("zeppelin/"):
            abs_import_path = os.path.join(os.getcwd(), import_path)
        else:
            if not parent_path:
                abs_import_path = os.path.join(os.getcwd(), "contracts", import_path)
            else:
                abs_import_path = os.path.join(parent_path, import_path)

        abs_import_path = os.path.abspath(abs_import_path)

        # Already handled
        if abs_import_path in self.processed_imports:
            return ""

        print("Expanding source code file", import_path)

        current_path = os.path.dirname(abs_import_path)

        with open(abs_import_path, "rt") as inp:
            source = inp.read()
            self.processed_imports.add(abs_import_path)
            return self.process_source(source, current_path)

    def process_source(self, src: str, parent_path: str):
        """Process Solidity source code and expand any import statement."""

        out = []

        for line in src.split("\n"):
            # Detect import statements, ghetto way
            if line.startswith('import "'):
                prefix, import_path, suffix = line.split('"')
                source = self.expand_file(import_path, parent_path=parent_path)
                out += source.split("\n")
            elif line.startswith("import '"):
                prefix, import_path, suffix = line.split("'")
                source = self.expand_file(import_path, parent_path=parent_path)
                out += source.split("\n")
            elif line.startswith('pragma'):
                # Only allow one pragma statement per file
                if self.pragma_processed:
                    continue
                else:
                    self.pragma_processed = True
            else:
                out.append(line)

        return "\n".join(out)


def expand_contract_imports(project: Project, contract_filename: str) -> Tuple[str, str]:
    """Expand Solidity import statements.

    :return: Tuple[final expanded source, set of processed filenames]
    """
    exp = Expander(project)
    return exp.expand_file(contract_filename), exp.processed_imports
