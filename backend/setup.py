from setuptools import setup, find_packages

setup(
    name='meu_backend',
    version='0.1',
    packages=find_packages(),  # isto acha 'server/', 'myspider_project/', etc
    # se quiser instalar dependências, pode por em "install_requires"
)