# robotframework-jmslibrary

## Getting started

### Installation

`pip install --upgrade robotframework-jmslibrary`

### Usage

```RobotFramework
*** Settings ***
Library  JMS

*** Test Cases ***
Send And Receive JMS Messages
    Create Producer    RobotQueue1    
    Send    Hello from Robot Framework
    Create Consumer    RobotQueue1
    Receive    ==    Hello from Robot Framework

Send JMS Messages
    Create Producer    RobotQueue4
    Send Message    Hello from Robot Framework
    Create Consumer    RobotQueue4
    Receive    ==    Hello from Robot Framework
```

