from setuptools import setup, find_packages

setup(
    name='pusher',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'pusher=pusher.main:main',
        ],
    },
)
