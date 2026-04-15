from setuptools import setup

setup(
    name="forest",
    version="1.0.0-alpha",
    description="Forest - Complete blue-team AI agent orchestration platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Forest AI",
    author_email="forest@example.com",
    url="https://github.com/forest-ai/forest",
    license="MIT",
    
    # Meta-package that imports all 5 core packages
    install_requires=[
        "forest-core>=1.0.0-alpha",
        "forest-training>=1.0.0-alpha",
        "forest-network>=1.0.0-alpha",
        "forest-audit>=1.0.0-alpha",
        "forest-dashboard>=1.0.0-alpha",
    ],
    
    python_requires=">=3.10",
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
