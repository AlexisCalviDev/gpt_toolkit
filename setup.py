from setuptools import setup, find_packages

setup(
    name='gpt_toolkit',
    version='0.0.0',
    packages=find_packages(),
    install_requires=[
        'openai==0.27.8',
        'requests==2.31.0',
        'rich==13.7.1'
    ],
    include_package_data=True,
    package_data={
        'gpt_toolkit': [],
    }
)