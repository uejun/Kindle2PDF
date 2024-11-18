from setuptools import setup, find_packages

setup(
    name='kindle2pdf',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
    ],
    author='Junya Ueda',
    author_email='ueda-junya@oruche.co.jp',
    description='Kindle2PDF project',
    url='https://github.com/uejun/kindle2pdf',
    entry_points={
        'console_scripts': [
            'kindle2pdf=kindle2pdf.cli.make_pdf:main',
        ],
    },
)