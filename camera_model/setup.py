"""Setup script for Camera Monitor library."""
from setuptools import setup, find_packages
import os


# Read README for long description
def read_file(filename):
    """Read file contents."""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


# Read version from package
def get_version():
    """Get version from __init__.py"""
    init_path = os.path.join('camera_monitor', '__init__.py')
    with open(init_path, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.0.1'


setup(
    name='camera-monitor',
    version=get_version(),
    author='Camera Monitor Team',
    author_email='',
    description='A flexible video monitoring library for Windows with hardware-accelerated encoding',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/camera-monitor',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Video :: Capture',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: Microsoft :: Windows',
    ],
    python_requires='>=3.10',
    install_requires=[
        'fastapi>=0.115.0',
        'uvicorn>=0.32.0',
        'pygrabber>=0.2',
        'opencv-python>=4.10.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'black>=24.0',
            'flake8>=6.0',
            'mypy>=1.0',
        ],
        'api': [
            'fastapi>=0.115.0',
            'uvicorn>=0.32.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'camera-monitor=camera_monitor.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords='camera video monitoring streaming recording ffmpeg hardware-encoding nvenc directshow',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/camera-monitor/issues',
        'Source': 'https://github.com/yourusername/camera-monitor',
        'Documentation': 'https://github.com/yourusername/camera-monitor#readme',
    },
)
