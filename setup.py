from setuptools import setup, find_packages
setup(
        name = 'caltechdata_api',
        version ='0.0.3',
        packages = find_packages(),
        install_requires=[
            'requests',
            'datacite'
        ]
    )
