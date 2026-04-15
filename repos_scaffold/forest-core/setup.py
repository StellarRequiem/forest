from setuptools import setup, find_packages

setup(
    name="forest-core",
    version="1.0.0-alpha",
    description="Forest CUS - Core orchestration engine for blue-team AI agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Forest AI",
    author_email="forest@example.com",
    url="https://github.com/forest-ai/forest-core",
    license="MIT",
    
    packages=find_packages(exclude=["tests", "examples"]),
    
    install_requires=[
        "langchain>=0.1.0",
        "langgraph>=0.0.20",
        "ollama>=0.1.0",
        "psutil>=5.9.0",
        "pydantic>=2.0.0",
    ],
    
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    
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
    
    entry_points={
        "console_scripts": [
            "forest-cus=forest_core.cli:main",
        ],
    },
)
