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
            'ncclient',
            'jinja2',
            'PTable'
            ],
        entry_points='''
            [console_scripts]
            tenx=tenx:cli
            '''
        )
