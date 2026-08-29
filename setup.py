import os

from setuptools import setup, find_packages

from sunsynk.version_info import Version

Version.generate()

with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'requirements.txt'))) as f:
    install_reqs = f.read().splitlines()

setup(
    name='sunsynk-api-client',
    version=Version.get(),
    description='API client for interacting with SunSynk APIs.',
    long_description='API client for interacting with SunSynk APIs.',
    author='James Ridgway',
    url='https://github.com/jamesridgway/sunsynk-api-client',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={'sunsynk': ['py.typed']},
    python_requires='>=3.13',
    install_requires=install_reqs,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Framework :: AsyncIO',
    ],
)
