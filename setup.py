import setuptools
from dodfminer.__version__ import __version__

def requirements_list():
    list_of_req = []
    with open('requirements.txt') as req:
        for line in req:
            list_of_req.append(line)

    return list_of_req


with open("README.md", "r") as fh:
    long_description = fh.read()

print(requirements_list())

setuptools.setup(
    name="dodfminer",
    version=__version__,
    author="KnEDLe",
    author_email="author@example.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UnB-KnEDLe/DODFMiner",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['dodfminer=dodfminer.run:run'],
    },
    install_requires=requirements_list(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    package_data={'dodfminer': ['extract/polished/acts/models/*.pkl']},
    include_package_data = True,
)
