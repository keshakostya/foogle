import setuptools

with open('Readme.md', 'r') as f:
    long_description = f.read()

with open("requirements.txt") as f:
    requirements = [x.strip() for x in f]

setuptools.setup(
    name='foogle',
    version='0.1',
    author='Konstantin Kozlov',
    description='Search engine',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
