from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get long description from README
long_description = (here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else "Procedure Automation Framework"

# Get version from package
def get_version():
    version_file = here / "flow_ctrl" / "__init__.py"
    with open(version_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "2.0.0"

setup(
    name="flow_ctrl",
    version=get_version(),
    description="Procedure Automation Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alveare-solutions/flow-ctrl",
    author="Del:Tango",
    author_email="alveare.solutions@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="automation, workflow, procedure, orchestration, cli",
    package_dir={"": "."},
    packages=find_packages(where=".", exclude=["tst", "tests.*", "build", "dist"]),
    include_package_data=True,
    python_requires=">=3.7, <4",
    install_requires=[
        "PyYAML>=5.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
            "wheel>=0.37.0",
            "twine>=3.8.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "flow_ctrl=flow_ctrl.src.cli.interface:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Del-Tango/FlowCTRL-Automation/issues",
        "Source": "https://github.com/Del-Tango/FlowCTRL-Automation",
    },
)

# CODE DUMP

