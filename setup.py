from distutils.core import setup

setup(
    name='GsFileLock',
    version='0.1.0',
    author='Evan Fosmark',
    author_email='me@evanfosmark.com',
    packages=['gsfilelock','gsfilelock.test'],
    url='https://github.com/JEdward7777/FileLock',
    license='LICENSE.txt',
    description='File locking library',
    long_description=open('README.txt').read(),
)
