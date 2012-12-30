from setuptools import setup
from setuptools import find_packages


long_description = (open('README.md').read()  )

def _static_files(prefix):
    return [prefix+'/'+pattern for pattern in [
        'markitup/*.*',
        'markitup/sets/*/*.*',
        'markitup/sets/*/images/*.png',
        'markitup/skins/*/*.*',
        'markitup/skins/*/images/*.png',
        'markitup/templates/*.*'
    ]]

setup(
    name='django-passbook',
    version='0.5.2', 
    description='djgnao passbook', 
    long_description=long_description,
    author='stephenmuss',
    author_email='',
    url='https://github.com/stephenmuss/django-passbook',
    packages=['passbook', ],
    zip_safe=False,
    include_package_data=True,
    package_data={'passbook': ['templates/passbook/*']} )
