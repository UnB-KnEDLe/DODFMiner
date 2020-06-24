import setuptools

def requirements_list():
    list_of_req = []
    with open('requirements.txt') as req:
        for line in req:
            list_of_req.append(line)

    return list_of_req

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dodfminer",
    version="1.0.0",
    author="Knedle",
    author_email="author@example.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UnB-KnEDLe/DODFMiner",
    packages=setuptools.find_packages(),
    entry_points = {
        'console_scripts': ['dodfminer=dodfminer.miner:run'],
    },
    install_requires=requirements_list(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)