import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="diana-star",
    version="0.0.2",
    author="Derek Merck",
    author_email="derek_merck@brown.edu",
    description="Diana scripts and infrastructure for task queues",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/derekmerck/diana-star",
    packages=setuptools.find_packages(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    license='MIT',
    install_requires=[
        'aenum',
        'ansible',
        'attrs',
        'bs4',
        'celery',
        'dateutils',
        'dill',
        'pillow',
        'redis',
        'ruamel.yaml',
        'pydicom',
        'requests'
    ]
)