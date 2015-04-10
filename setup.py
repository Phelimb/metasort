from setuptools import setup
 
setup(
    name='metasort',
    version='0.3.6.3',
    packages=['metasort', ],
    license='MIT',
    url='http://github.com/phelimb/metasort',
    description='Filter reads based on taxonomy assignment from OneCodex.',    
    author='Phelim Bradley, Gil Goncalves',
    author_email='wave@phel.im, lursty@gmail.com',
    install_requires=["requests==2.5.3","Biopython","onecodex","Flask==0.10.1"],
    entry_points={
        'console_scripts': [
            'metasort = metasort.cli:main',
        ]
    }
)