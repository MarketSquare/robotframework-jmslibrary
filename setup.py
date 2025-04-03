# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['JMS']

package_data = \
{'': ['*']}

install_requires = \
['jpype1>=1.4.1,<2.0.0',
 'robotframework',
 'robotframework-assertion-engine>=1.1.1,<2.0.0']

setup_kwargs = {
    'name': 'robotframework-jmslibrary',
    'version': '0.2.0',
    'description': '',
    'long_description': '# robotframework-jmslibrary\n\n## Getting started\n\n### Installation\n\n`pip install --upgrade robotframework-jmslibrary`\n\n### Usage\n\n```RobotFramework\n*** Settings ***\nLibrary  JMS\n\n*** Test Cases ***\nSend And Receive JMS Messages\n    Create Producer    RobotQueue1    \n    Send    Hello from Robot Framework\n    Create Consumer    RobotQueue1\n    Receive    ==    Hello from Robot Framework\n\nSend JMS Messages\n    Create Producer    RobotQueue4\n    Send Message    Hello from Robot Framework\n    Create Consumer    RobotQueue4\n    Receive    ==    Hello from Robot Framework\n```\n\n',
    'author': 'Many Kasiriha',
    'author_email': 'many.kasiriha@dbschenker.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.1,<4.0',
}


setup(**setup_kwargs)
