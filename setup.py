from setuptools import setup, find_packages

setup(
	name="wristwatch",
	version="1.0.0",
	packages=find_packages(),
	install_requires=[
		"beautifulsoup4",
		"selenium",
		"rookiepy",
	],
	entry_points={
		"console_scripts": [
			"wristwatch = wristwatch.wristwatch:main"
		]
	}
)