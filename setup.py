from setuptools import setup


setup(
        name = 'tenx',
        version = '1.0',
        py_modules = ['tenx'],
        install_requires =  [
            'click',
            'untangle',
            'pyaml',
            'ncclient'
            ],
        entry_points='''
            [console_script]
            tenx=tenx:cli
            '''
        )
