import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stackedwaterfalls",
    version="0.7",
    author="Prash",
    author_email="prash@mit.edu",
    description="A small utility to create stacked waterfalls using matplotlib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/askprash/stackedwaterfall",
    project_urls={
        "Bug Tracker": "https://github.com/askprash/stackedwaterfall/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "stackedwaterfalls"},
    packages=setuptools.find_packages(where="stackedwaterfalls"),
    python_requires=">=3.6",
)
