from setuptools import setup, find_packages

setup(
    name="forest-dashboard",
    version="1.0.0-alpha",
    description="Forest Dashboard - Real-time decision visualization with Streamlit",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Forest AI",
    author_email="forest@example.com",
    url="https://github.com/forest-ai/forest-dashboard",
    license="MIT",
    
    packages=find_packages(exclude=["tests", "examples"]),
    
    install_requires=[
        "streamlit>=1.20.0",
        "plotly>=5.0.0",
        "pandas>=1.5.0",
        "forest-core>=1.0.0-alpha",
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
            "forest-dashboard=forest_dashboard.cli:main",
        ],
    },
)
