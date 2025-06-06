# robotframework-jmslibrary

Robot Framework library for sending and receiving JMS messages to different JMS providers like ActiveMQ and WebLogic.

📕 [Keyword Documentation](https://marketsquare.github.io/robotframework-jmslibrary/JMS.html)

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

