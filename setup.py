from setuptools import setup, find_packages

setup(
    name="VisioNomicon",
    version="0.1.5",
    author="Rehan Rana",
    author_email="visionomicon@rehanzo.com",
    description="A utility leveraging GPT-4o for image file renaming based on content.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rehanzo/visionomicon",
    packages=find_packages(),
    install_requires=[
        "requests",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "VisioNomicon=VisioNomicon.main:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    keywords="gpt-4 gpt-4v gpt-4o openai renaming images",
)
