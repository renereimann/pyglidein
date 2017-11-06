from setuptools import setup, find_packages

setup(
    name='pyglidein',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Some python scripts to launch HTCondor glideins',
    url='https://github.com/WIPACrepo/pyglidein',
    author='WIPAC',
    author_email='contact-us@icecube.wisc.edu',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='htcondor htc glidein',
    packages=find_packages(),
    install_requires=['minio', 'tornado'],
    package_data={
        'pyglidein': ['glidein_start.sh', 'log_shipper.sh', 'os_arch.sh']
    },
    entry_points={
        'console_scripts': [
            'pyglidein_client=pyglidein.client:main',
            'pyglidein_server=pyglidein.server:main'
        ]
    },
    python_requires='>=2.7'
)
