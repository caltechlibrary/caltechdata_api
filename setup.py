#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io, json
import os
import sys
import glob
from shutil import rmtree

from setuptools import find_packages, setup, Command


def read(fname):
    with open(fname, mode="r", encoding="utf-8") as f:
        src = f.read()
    return src


def package_files(package, directory):
    os.chdir(package)
    paths = glob.glob(directory + "/**", recursive=True)
    os.chdir("..")
    return paths


codemeta_json = "codemeta.json"

# Let's pickup as much metadata as we need from codemeta.json
with open(codemeta_json, mode="r", encoding="utf-8") as f:
    src = f.read()
    meta = json.loads(src)

# Let's make our symvar string
version = meta["version"]

# Now we need to pull and format our author, author_email strings.
author = ""
author_email = ""
for obj in meta["author"]:
    given = obj["givenName"]
    family = obj["familyName"]
    email = obj["email"]
    if len(author) == 0:
        author = given + " " + family
    else:
        author = author + ", " + given + " " + family
    if len(author_email) == 0:
        author_email = email
    else:
        author_email = author_email + ", " + email
description = meta["description"]
url = meta["codeRepository"]
download = meta["downloadUrl"]
license = meta["license"]
name = meta["name"]

REQUIRES_PYTHON = ">=3.6.0"

# What packages are required for this module to be executed?
REQUIRED = ["requests", "datacite>1.1.0", "tqdm>=4.62.3", "pyyaml", "s3fs"]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

files = package_files("caltechdata_api", "vocabularies")
files.append("vocabularies.yaml")

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = description

# Load the package's __version__.py module as a dictionary.
about = {}
if not version:
    with open(os.path.join(here, NAME, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = version


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel distribution…")
        os.system("{0} setup.py sdist bdist_wheel ".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        sys.exit()


# Where the magic happens:
setup(
    name=name,
    version=about["__version__"],
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=author,
    author_email=author_email,
    python_requires=REQUIRES_PYTHON,
    url=url,
    packages=find_packages(exclude=("tests",)),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],
    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    package_data={name: files},
    license=license,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    # $ setup.py publish support.
    cmdclass={
        "upload": UploadCommand,
    },
)
