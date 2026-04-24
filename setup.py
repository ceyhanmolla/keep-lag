from setuptools import setup, find_packages

setup(
    name="keeplag",
    version="0.1.0",
    description="Modern HTTP stress test tool",
    author="KeepLag",
    py_modules=["keeplag"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "keeplag=keeplag:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)