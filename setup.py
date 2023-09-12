"""
Open Command Prompt in this file's directory and then type: python setup.py install
"""

from setuptools import setup

setup(
    name='Newgrounds-Music-Downloader',
    version='1.0.0',
    description='A Python Script to download Newgrounds Music using a Given Song ID!',
    author='Fesuoy1',
    download_url='https://github.com/Fesuoy1/Newgrounds-Music-Downloader/releases/download/initial/Newgrounds_Music_Downloader.py',
    py_modules=['Newgrounds_Music_Downloader'],
    install_requires=[
        'aiofiles',
        'aiohttp',
        'bs4',
        'msgpack',
        'pycached',
        'requests',
        'requests-cache',
        'ujson',
        'customtkinter',
        ],
        entry_points={
        'console_scripts': [
            'newgrounds-downloader=Newgrounds_Music_Downloader:main',
        ],
     },
 )
