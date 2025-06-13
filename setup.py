from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="astroshield-integration-package",
    version="0.1.0",
    author="Jack Al-Kahwati",
    author_email="jack@lattis.io",
    description="Integration package for AstroShield space situational awareness platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jackalkahwati/astroshield-integration-package",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "confluent-kafka>=2.0.0",
        "python-dateutil>=2.8.2",
        "urllib3>=1.26.0",
        "python-dotenv>=1.0.0",
        "kafka-python>=2.0.0",
        "threading2>=0.3.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "mock>=5.0.0",
        ],
    },
) 