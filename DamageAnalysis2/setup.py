"""Setup script for League of Legends Analytics package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "League of Legends performance analytics and damage calculation framework"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "requests>=2.28.0",
        "pydantic>=1.10.0",
        "python-dotenv>=0.19.0",
    ]

setup(
    name="lol-analytics",
    version="1.0.0",
    author="Timothy Kim",
    description="League of Legends performance analytics and damage calculation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
        ],
        "web": [
            "fastapi>=0.85.0",
            "uvicorn>=0.18.0",
            "streamlit>=1.12.0",
        ],
        "ml": [
            "scikit-learn>=1.1.0",
            "scipy>=1.9.0",
            "statsmodels>=0.13.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lol-analytics=lol_analytics.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "lol_analytics": [
            "data/*.json",
            "data/*.yaml",
        ],
    },
    zip_safe=False,
)