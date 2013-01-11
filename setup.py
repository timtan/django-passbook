from setuptools import setup
from setuptools import find_packages


long_description = (open('README.md').read()  )


setup(
    name='django-passbook',
    version='0.5.4', 
    description='djgnao passbook', 
    long_description=long_description,
    author='stephenmuss',
    author_email='',
    url='https://github.com/stephenmuss/django-passbook',
    packages=['passbook', ],
    zip_safe=False,
    include_package_data=True,
    package_data={'passbook': ['templates/passbook/*']} )
