from setuptools import find_packages, setup
from pathlib import Path

dir = Path(__file__).parent
with open(dir / "README.md", "r") as f:
    long_description = f.read()

setup(
    name="proofaday",
    version="0.2.6",
    author="Wolf Honoré",
    author_email="wolfhonore@gmail.com",
    description="Print random proofs from ProofWiki",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/whonore/proofaday",
    packages=find_packages(),
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3 :: Only",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=[
        "requests~=2.22.0",
        "beautifulsoup4~=4.8.0",
        "pylatexenc~=2.1",
        "python-daemon~=2.2.0",
        "click~=7.1.0",
    ],
    entry_points={
        "console_scripts": [
            "proofaday=proofaday.proofaday:main",
            "dproofaday=proofaday.daemon_cli:main",
        ],
    },
)
