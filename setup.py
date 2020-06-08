import setuptools
from dodfminer.requirements_list import requirements_list

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dodfminer",
    version="0.0.1",
    author="Knedle",
    author_email="author@example.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UnB-KnEDLe/DODFMiner",
    packages=setuptools.find_packages(),
    install_requires=requirements_list(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)