from setuptools import setup, find_packages

"""
Revision History

0.1.0 - 2020 Dec 29 - Original release for PSM Hackathon manuscript
"""

requirements = [
    'antelope_core[XML]==0.1.3rc4',  # broken in 0.1.4 in term_manager bc of a bad pop
    'antelope_foreground>=0.1.3rc1',
    'lca_disclosures==0.2.0rc2',
    'requests>=2.23.0'
]


setup(
    name='antelope_epa',
    version="0.1.0",
    packages=find_packages(),
    author="Brandon Kuczenski",
    author_email="bkuczenski@ucsb.edu",
    license=open('LICENSE').read(),
    #entry_points = {
    #   'console_scripts': [
    #   ]
    #},
    install_requires=requirements,
    url="https://github.com/bkuczenski/antelope_epa",
    long_description=open('README.md').read(),
    description='Software for building LCA models from foreground specifications, created for the EPA PSM hackathon',
    keywords=['LCA', 'Life Cycle Assessment', 'Foreground system',
              'Foreground model'],
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
