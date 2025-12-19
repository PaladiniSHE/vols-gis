from setuptools import setup, find_packages

requires = [
    'pyramid>=2.0',
    'waitress>=2.1.0',
    'sqlalchemy>=2.0.0',
    'geoalchemy2>=0.14.0',
    'psycopg2-binary>=2.9.0',
    'pydantic>=2.0.0',
    'pyjwt>=2.8.0',
    'passlib[bcrypt]>=1.7.4',
]

tests_require = [
    'pytest>=7.4.0',
    'pytest-cov>=4.1.0',
]

setup(
    name='vols-gis',
    version='0.1.0',
    description='инималистичный аналог NextGIS Web для учета С',
    author='',
    author_email='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require={
        'testing': tests_require,
    },
    entry_points={
        'paste.app_factory': [
            'main = vols_gis:main',
        ],
    },
)
