from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent
about = {}

with open(here / "src" / "aioauth" / "__version__.py", "r") as f:
    exec(f.read(), about)

with open("README.md") as readme_file:
    readme = readme_file.read()


def read_requirements(path):
    try:
        with path.open(mode="rt", encoding="utf-8") as fp:
            return list(filter(bool, (line.split("#")[0].strip() for line in fp)))
    except IndexError:
        raise RuntimeError(f"{path} is broken")


base_requirements = read_requirements(here / "requirements" / "base.txt")
test_requirements = read_requirements(here / "requirements" / "test.txt")

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    license=about["__license__"],
    python_requires=">=3.6.0",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=base_requirements,
    tests_require=test_requirements,
    extras_require={"test": test_requirements},
    include_package_data=True,
    keywords="aioauth",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    test_suite="tests",
    zip_safe=False,
    project_urls={"Source": about["__url__"]},
)
