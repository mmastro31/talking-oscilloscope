from setuptools import setup

setup(name='talking-oscilloscope',
    version = '1.0',
    description='Oscilloscope with auditory feedback',
    author='mmastro31',
    author_email='mm9587@nyu.edu',
    url='https://github.com/mmastro31/talking-oscilloscope',
    install_requires=['adafruit-circuitpython-ina260','adafruit-circuitpython-rgb-display',],
    py_modules = ['oscilloscope']
    )

