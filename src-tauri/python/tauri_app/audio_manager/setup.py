"""
安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="audio-manager",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="实时音频监控库，支持麦克风和系统音频",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/audio-manager",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.7",
    install_requires=[
        "sounddevice>=0.4.0",
        "numpy>=1.19.0",
        "pycaw>=20181226",
        "comtypes>=1.1.0",
    ],
)