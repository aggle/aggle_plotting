from setuptools import setup

setup(
     # Needed to silence warnings (and to be a worthwhile package)
    name='agplot',
    url='https://github.com/aggle/aggle_plotting',
    author='Jonathan Aguilar',
    author_email='jaguilar@stsci.edu',
    # Needed to actually package something
    packages=['agplot'],
    # Needed for dependencies
    install_requires=['matplotlib'],
    # *strongly* suggested for sharing
    version='0.1',
    # The license can be anything you like
    license='MIT',
    description='Custom plotting styles',
    # We will also need a readme eventually (there will be a warning)
    long_description=open('README.md').read(),   
)
