from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.2'
DESCRIPTION = 'A flexiable web framework'
LONG_DESCRIPTION = 'A package that allows to build simple web application that use json db'

# Setting up
setup(
    name="tesla@web2",
    version=VERSION,
    author="Jafar idris",
    author_email="<jafaridris82@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['uuid','jinja2', 'tesla-admin', 'argon2-cffi', 'waitress'],
    keywords=['python', 'web', 'auth'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    include_package_data=True,

)
