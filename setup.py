#!/usr/bin/env python3
from pathlib import Path

import setuptools
from setuptools import setup

this_dir = Path(__file__).parent

requirements = []
requirements_path = this_dir / "requirements.txt"
if requirements_path.is_file():
    with open(requirements_path, "r", encoding="utf-8") as requirements_file:
        requirements = requirements_file.read().splitlines()

module_name = "wyoming_hailo_whisper"
module_dir = this_dir / module_name
data_files = []

version_path = module_dir / "VERSION"
data_files.append(version_path)
version = version_path.read_text(encoding="utf-8").strip()

# -----------------------------------------------------------------------------

setup(
    name=module_name,
    version=version,
    description="Wyoming Server for Hailo whisper",
    url="",
    author="mpeex",
    author_email="",
    license="MIT",
    packages=setuptools.find_packages(),
    package_data={module_name: [str(p.relative_to(module_dir)) for p in data_files]},
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="rhasspy wyoming hailo whisper stt",
    entry_points={
        "console_scripts": ["wyoming-hailo-whisper = wyoming_hailo_whisper.__main__:run"]
    },
)
