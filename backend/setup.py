"""
Setup script for SurBlend backend
"""

from setuptools import setup, find_packages

with open("../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="surblend",
    version="1.0.0",
    author="Your Company",
    author_email="support@yourcompany.com",
    description="Fertilizer Blending and Quoting System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shrimpmann/SurBlend-Apps",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "surblend=app.main:main",
            "surblend-init=app.services.startup:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["templates/*", "static/*"],
    },
)