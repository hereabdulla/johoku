from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in johoku/__init__.py
from johoku import __version__ as version

setup(
	name="johoku",
	version=version,
	description="Customizations for Johoku",
	author="TEAMPRO",
	author_email="erp@groupteampro.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
