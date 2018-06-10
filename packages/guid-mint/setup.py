import setuptools
from shutil import copyfile

copyfile("../../README.md", "README.md")
# copyfile("../requirements.txt", "requirements.txt")

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("../../requirements.txt", "r") as fh:
    reqs = fh.read().splitlines()

setuptools.setup(
    name="guid-mint",
    version="0.0.2",
    author="Derek Merck",
    author_email="derek_merck@brown.edu",
    description="Global unique ID and pseudonym generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/derekmerck/diana-star",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    license='MIT',
    install_requires=reqs
)