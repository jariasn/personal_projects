from setuptools import find_packages, setup

setup(
    name='cryptonn',
    packages=find_packages(include=['cryptonn']),
    version='0.1.0',
    description='Cryptocurrency trading bot using machine learning', 
    author='Joaquin Arias',
    install_requires=[
        "requests",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)