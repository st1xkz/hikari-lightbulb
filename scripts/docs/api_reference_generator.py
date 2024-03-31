# -*- coding: utf-8 -*-
# Copyright (c) 2023-present tandemdude
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import pathlib
import typing as t

API_REFERENCES_DIRECTORY = "docs", "source", "api-references"


def is_package(path: pathlib.Path) -> bool:
    return path.is_dir() and (path / "__init__.py").is_file()


class Module:
    def __init__(self, path: pathlib.Path) -> None:
        self.path = path

    def write(self) -> bool:
        # Ignore the module if it contains a generation ignore comment in the first 10 lines
        with open(self.path) as module:
            content = module.readlines(10)
            if any("# api_reference_gen::ignore" in line for line in content):
                return False

        parts = self.path.parts

        api_reference_dir_path = str(os.path.join(*API_REFERENCES_DIRECTORY, *parts[:-1]))
        os.makedirs(api_reference_dir_path, exist_ok=True)

        with open(os.path.join(api_reference_dir_path, parts[-1].replace(".py", ".rst")), "w") as fp:
            module_name = ".".join(parts)[:-3]
            fp.write(
                "\n".join(
                    [
                        "=" * len(module_name),
                        module_name,
                        "=" * len(module_name),
                        "",
                        f".. automodule:: {module_name}",
                        "    :members:",
                    ]
                )
            )

        return True


class Package:
    def __init__(
        self, path: pathlib.Path, header_override: t.Optional[str] = None, child_prefix: t.Optional[str] = None
    ) -> None:
        self.path = path
        self.header_override = header_override
        self.child_prefix = [child_prefix] if child_prefix else []

        self.packages = []
        self.modules = []

    def find_children(self) -> None:
        for item in self.path.iterdir():
            if is_package(item):
                self.packages.append(Package(item))
                continue

            if item.name.startswith("_") or not item.name.endswith(".py"):
                continue

            self.modules.append(Module(item))

    def write(self) -> bool:
        written_packages = []
        written_modules = []

        self.find_children()
        for package in self.packages:
            if package.write():
                written_packages.append(package)
        for module in self.modules:
            if module.write():
                written_modules.append(module)

        # If no pages were written for any subpackage or submodule then we don't need a page for this package
        if not written_packages and not written_modules:
            return False

        parts = self.path.parts

        api_reference_dir_path = str(os.path.join(*API_REFERENCES_DIRECTORY, *parts[:-1]))
        os.makedirs(api_reference_dir_path, exist_ok=True)

        with open(os.path.join(api_reference_dir_path, parts[-1] + ".rst"), "w") as fp:
            package_name = self.header_override or ".".join(parts)

            package_lines = [
                f"    {'/'.join([*self.child_prefix, self.path.name, *package.path.relative_to(self.path).parts])}"
                for package in written_packages
            ]
            module_lines = [
                f"    {'/'.join([*self.child_prefix, self.path.name, *module.path.relative_to(self.path).parts])}"[:-3]
                for module in written_modules
            ]

            lines = [
                "=" * len(package_name),
                package_name,
                "=" * len(package_name),
                "",
            ]

            if package_lines:
                lines.extend(["**Subpackages:**", "", ".. toctree::", "    :maxdepth: 1", "", *sorted(package_lines), ""])
            if module_lines:
                lines.extend(["**Submodules:**", "", ".. toctree::", "    :maxdepth: 1", "", *sorted(module_lines), ""])

            fp.write("\n".join(lines).strip())

        return True


def run() -> None:
    Package(
        pathlib.Path("lightbulb"), header_override="API Reference", child_prefix=API_REFERENCES_DIRECTORY[-1]
    ).write()
    os.rename(
        os.path.join(*API_REFERENCES_DIRECTORY, "lightbulb.rst"),
        os.path.join(*API_REFERENCES_DIRECTORY[:-1], "api-reference.rst"),
    )


if __name__ == "__main__":
    run()
