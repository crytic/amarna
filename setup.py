from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="amarna",
    version="0.1.3",
    description="Amarna is a static-analyzer for the Cairo programming language.",
    url="https://github.com/crytic/amarna",
    author="Trail of Bits",
    license="AGPL-3.0",
    packages=find_packages(),
    package_data={"amarna": ["grammars/cairo.lark"]},
    install_requires=[
        "lark>=1.1.2",
        "pydot>=1.4.2",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "amarna=amarna.command_line:main",
        ],
    },
)
