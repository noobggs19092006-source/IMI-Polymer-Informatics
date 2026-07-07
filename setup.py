from setuptools import setup, find_packages
from version import __version__

setup(
    name="polymer-informatics",
    version=__version__,
    description="Automated simulation and ML pipeline for polymer capacitance",
    url="https://github.com/zapzapzap12v/Polymer_Informatics",
    author="Your Team",
    python_requires=">=3.10",
    packages=find_packages(),
)
