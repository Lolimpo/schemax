from setuptools import find_packages, setup


def find_required():
    with open("requirements.txt") as f:
        return f.read().splitlines()


def find_dev_required():
    with open("requirements-dev.txt") as f:
        return f.read().splitlines()


setup(
    name="schemax",
    version="v0.0.0rc1",
    description="district42 to JSON-Schema translator and vise versa",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Nikita Mikheev",
    author_email="thelol1mpo@gmail.com",
    python_requires=">=3.10",
    url="https://github.com/lolimpo/schemax",
    license="Apache-2.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    package_data={"schemax": ["py.typed"]},
    install_requires=find_required(),
    tests_require=find_dev_required(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
    ],
)
