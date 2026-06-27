from setuptools import setup, find_packages

setup(
    name='email_service',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Flask==2.1.1',
        'requests==2.27.1',
    ],
    test_suite='tests',
)
