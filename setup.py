# -*- coding: utf-8 -*-

import importlib
import importlib.util
import os
import setuptools

"""Read the plugin version from the source code."""
module_path = os.path.join(
    os.path.dirname(__file__), "inventree_bambu", "__init__.py"
)
spec = importlib.util.spec_from_file_location("inventree_bambu", module_path)
inventree_bambu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventree_bambu)

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()


setuptools.setup(
    name="inventree-bambu-plugin",
    version=inventree_bambu.PLUGIN_VERSION,
    author="James Todd",
    author_email="james.todd@nottingham.ac.uk",
    description="BambuLab 3D Printing Machine Support for InvenTree",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="inventree bambu lab 3d printer printing inventory",
    url="https://github.com/psxjt5/inventree-bambu-plugin",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=[
        "inventree-3d-printing"
    ],
    setup_requires=[
        "wheel",
        "twine",
    ],
    python_requires=">=3.9",
    entry_points={
        "inventree_plugins": [
            "Bambu3DPlugin = inventree_bambu.bambu3d_plugin:Bambu3DPlugin"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Framework :: InvenTree",
    ],
)
