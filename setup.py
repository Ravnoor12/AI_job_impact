''' setup file to define the package and its dependencies along with configuration of project'''

from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:

    requirements_lst:List[str] = []
    try:
        with open('requirement.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                requirement = line.strip()  
                if requirement and not requirement.startswith('#') and requirement != '-e .':
                    requirements_lst.append(requirement)
    except FileNotFoundError:
        print(f"Error: The requirement file  was not found.")
    return requirements_lst

# print(get_requirements())

setup(
    name='mlproject',
    version='0.0.1',
    author='Ravnoor Singh',
    author_email='ravnoor12@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements()
)