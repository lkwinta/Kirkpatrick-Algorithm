from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().split('\n')

setup(
    name='kirkpatrick',
    description='Implementation of Kirkaptrick algorim for localizing point in polygon',
    long_description_content_type='text/markdown',
    author='Wiktor Warzecha, Łukasz Kwinta',
    packages=['kirkpatrick_algorithm'],
    python_requires='>=3.8',
    install_requires=requirements,
)
