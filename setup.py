from setuptools import setup

setup(
        name = 'tenx',
        version = '1.0',
        py_modules = ['tenx'],
        install_requires =  [
            'click',
            'requests',
            'untangle',
            'pyaml',
            'ncclient'
            ],
        entry_points='''
            [console_scripts]
            tenx=tenx:cli
            '''
        )
