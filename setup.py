from setuptools import setup
 
setup(
    name='metasort',
    version='0.1',
    packages=['metasort', ],
    license='MIT',
    description='Filter reads based on taxonomy assignment from OneCodex.',
    long_description=open('README.md').read(),
    author='Phelim Bradley, Gil Goncalves',
    author_email='wave@phel.im, lursty@gmail.com',
    install_requires=["Flask==0.10.1","requests==2.5.3","Biopython","gunicorn"],
    entry_points={
        'console_scripts': [
            'metasort = metasort.cli:main',
        ]
    }
)