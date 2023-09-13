import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

def get_requirements():
    with open('requirements.txt', 'r') as f:
        return f.readlines()

setup(
    name='fbo-scraper',
    version='1.2.0',
    description="This project gathers Information Technology (IT) solicitations that are posted by the US Federal Government on beta.sam.gov.",
    long_description="This project gathers Information Technology (IT) solicitations that are posted by the US Federal Government on beta.sam.gov.",
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
    ],
    author='Adam Buckingham',
    author_email='abuckingham@idoxsolutions.com',
    url='https://github.com/GSA/srt-fbo-scraper',
    keywords='python package',
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'fbo_scraper=fbo_scraper.main:actual_main',
        ],
    },
)