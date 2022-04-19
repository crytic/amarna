from setuptools import setup, find_packages

setup(
    name="amarna",
    version="0.1",
    description="Amarna is a static-analyzer for the Cairo programming language.",
    author="Trail of Bits",
    license="",
    packages=find_packages(),
    package_data={"amarna": ["grammars/cairo.lark"]},
    install_requires=[
        "lark",
    ],
    license="AGPL-3.0",
    entry_points={
        "console_scripts": [
            "amarna=amarna.command_line:main",
        ],
    },
)
