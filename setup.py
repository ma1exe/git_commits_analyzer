#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="git-dev-productivity",
    version="1.0.0",
    description="Анализатор продуктивности разработчиков на основе Git-репозитория",
    author="Ваше имя",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "gitpython>=3.1.0",
        "flask>=2.0.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "pygal>=2.4.0",
    ],
    entry_points={
        "console_scripts": [
            "git-dev-productivity=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.7",
)
