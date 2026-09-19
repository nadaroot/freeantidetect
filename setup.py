from setuptools import setup, find_packages

setup(
    name="root-detect",
    version="1.0.0",
    description="Autonomous Standalone Antidetect Browser CLI & TUI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="nadaroot",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "rootdetect": [
            "extension/*",
            "extension/manifest.json",
            "extension/inject.js",
            "extension/background.js"
        ]
    },
    install_requires=[
        "rich>=13.0.0",
        "requests>=2.28.0"
    ],
    entry_points={
        "console_scripts": [
            "antidetect=rootdetect.cli:main",
            "rootdetect=rootdetect.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
