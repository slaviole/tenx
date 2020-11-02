from setuptools import setup

setup(
        name = 'mytenx',
        version = '1.0',
        py_modules = ['mytenx'],
        install_requires =  [
            'click',
            'requests',
            'untangle',
            'pyaml',
            'ncclient',
            'jinja2',
            'prettytable'
            ],
        entry_points='''
            [console_scripts]
            mytenx=mytenx:cli
            '''
        )
