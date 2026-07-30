# CHANGELOG
## v0.5.0
### Features
### Bugfix
- Fix of issue: [Library can't be used during robot --dry-run](https://github.com/MarketSquare/robotframework-jmslibrary/issues/6)

## v0.4.0
### Features

- Added parameter to set path to jvm library file. \
This configuration is required in special situations when the jvm library file is not automatically detected.

### Note
Some existing keywords are marked as deprecated and will be removed in a future release.


## v0.3.0
### Features
- Added support for JMS Topics
- Added basic support for JMS properties
- Added support for BytesMessages
- Internal Refactoring

### Note
Some existing keywords are marked as deprecated and will be removed in a future release.

## v0.2.0
### Features
- ActiveMQ and WebLogic Support
    - Connect to both ActiveMQ and WebLogic JMS providers with a single library.
    - Easily switch between providers using the type argument.

- Flexible Connection Configuration
    - Configure server address, port, username, password, connection factory, and timeout.
    - Customizable classpath for JMS JARs, supporting both default and user-supplied values.

- Producer and Consumer Management
    - Create and manage multiple producers and consumers for different queues.
    - Support for both queue and topic destinations.

- Message Operations
    - Create, send, and receive text messages.
    - Send messages directly to producers or queues.
    - Receive messages with assertion support for test validation.
    - Clear queues and receive all messages as a list.

- Assertion Integration
    - Built-in assertion operators and formatters for validating message content in Robot Framework tests.
- Timeout Control
    - Set global or per-keyword timeouts for message operations.

- Connection Lifecycle Management
    - Start, stop, and close JMS connections cleanly.
    - JVM shutdown support for resource cleanup.

### Example Usage
```
*** Settings ***
Library  JMS

*** Test Cases ***
Send And Receive JMS Messages
    Create Producer    RobotQueue1    
    Send    Hello from Robot Framework
    Create Consumer    RobotQueue1
    Receive    ==    Hello from Robot Framework
```

### Notes
Requires Java and appropriate JMS provider JARs in the classpath.
Compatible with Robot Framework and supports advanced assertion features for message validation.

For more details, see the library documentation or the docstring in the JMS class.
