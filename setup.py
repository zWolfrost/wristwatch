from setuptools import setup, find_packages

setup(
	name="wristwatch",
	author="zWolfrost",
	version="1.3.0",
	description="Yet another Python watcher for website updates.",
	long_description=open("README.md").read(),
	long_description_content_type="text/markdown",
	url="https://github.com/zWolfrost/wristwatch",
	packages=find_packages(),
	install_requires=[
		"beautifulsoup4>=4.11.0",
		"selenium>=4.19.0",
		"browser-cookie3>=0.19.0",
		"chime>=0.7.0"
	],
	entry_points={
		"console_scripts": [
			"wristwatch = wristwatch.wristwatch:main"
		]
	}
)