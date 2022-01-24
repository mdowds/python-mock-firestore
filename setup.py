import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mock-firestore",
    version="0.11.0",
    author="Matt Dowds",
    description="In-memory implementation of Google Cloud Firestore for use in tests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mdowds/mock-firestore",
    packages=setuptools.find_packages(),
    test_suite='',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        "License :: OSI Approved :: MIT License",
    ],
)