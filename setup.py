"""Setup script for Cortex Desktop Assistant."""

from setuptools import setup, find_packages

# Read the README for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name="cortex-desktop-assistant",
    version="1.5.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful, modular, and extensible voice assistant with multiple TTS engine support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cortex-desktop-assistant",
    packages=find_packages(),
    package_data={
        "cortex": ["*.yaml", "*.json"],
    },
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cortex=cortex.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
)
