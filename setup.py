from setuptools import setup, find_packages

setup(
    name="docit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rumps>=0.4.0",
        "pynput>=1.7.6",
        "sounddevice>=0.4.6",
        "soundfile>=0.12.1",
        "numpy>=1.24.0",
    ],
    entry_points={
        "console_scripts": [
            "docit=run:main",
        ],
    },
)
