from setuptools import setup, find_packages

setup(
    name="atomic_search",
    version="0.1.0",
    description="A Python package for extracting and detecting malicious JavaScript syntax through atomic and molecule search.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Alfin Gusti Alamsyah",
    author_email="alfinalamsyahhh@gmail.com",
    url="https://github.com/aflinxh/atomic_search",
    packages=find_packages(exclude=["utils", "utils.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Application Frameworks"
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=8.3.3",
            "invoke>=2.2.0"
        ]
    },
    keywords="malicious code detection, JavaScript analysis, obfuscation, feature extraction",
)