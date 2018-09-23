#!/usr/bin/env python
# encoding=utf-8

from setuptools import setup

setup(name='mwtextextractor',
      version='0.1.3',
      description='Extracts body text from MediaWiki wikitext by stripping off templates, html tags, tables, headers, etc.',
      long_description=(
          open('README.rst').read()
      ),
      author='Dan Michael O. Heggø',
      author_email='danmichaelo@gmail.com',
      url='https://github.com/danmichaelo/mwtextextractor',
      license='MIT',
      keywords='mediawiki',
      install_requires=['lxml', 'mwtemplates'],
      packages=['mwtextextractor'],
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
      ]
      )
