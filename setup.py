from setuptools import setup, find_packages

setup(
    name='gpt_toolkit',
    version='0.0.10',
    packages=find_packages(),
    install_requires=[
        'openai==0.27.8',
        'requests==2.31.0',
        'rich==13.7.1',
        'PyMySQL==1.1.0',
        'paramiko==3.3.1',
        'sshtunnel==0.4.0',
        'PyYAML==6.0.1',
        'sqlalchemy==2.0.27'
    ],
    include_package_data=True,
    package_data={
        'gpt_toolkit': [],
    }
)