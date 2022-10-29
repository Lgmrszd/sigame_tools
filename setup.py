from setuptools import setup

setup(
    name="SIGameTools",
    version="0.0.1",
    author="Lgmrszd",
    author_email="lgmrszd@gmail.com",
    packages=["sigame_tools"],
    entry_points= {
        "console_scripts": ["sigame-tools=sigame_tools.cli:main"]
    }
    # scripts=["bin/sigame-tools"]
)
