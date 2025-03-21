from setuptools import setup, find_packages

# Read the contents of the README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="validiz",
    version="1.0.0",
    description="A Python client library for the Validiz Email Validation API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shehryar Sohail",
    author_email="shehryardev@paklogics.com",
    url="https://github.com/shehryardev/validiz-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=open("requirements.txt").read().splitlines(),
    keywords="email, validation, api, client, async",
) 