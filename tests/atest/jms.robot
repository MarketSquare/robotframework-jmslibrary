*** Settings ***
Library  JMS

*** Test Cases ***
Send And Receive JMS Text Message using Queue
    Create Producer    RobotQueue1    
    Send    Hello from Robot Framework
    Create Consumer    RobotQueue1
    Receive    ==    Hello from Robot Framework

Send JMS Text Message using Queue
    Create Producer    RobotQueue4
    Send Message    Hello from Robot Framework
    Create Consumer    RobotQueue4
    Receive    ==    Hello from Robot Framework

Send And Receive JMS Text Message using Topic
    Create Producer Topic   RobotTopic1
    Create Consumer Topic   RobotTopic1
    Send    Hello from Robot Framework
    Create Consumer Topic    RobotTopic1
    Receive    ==    Hello from Robot Framework

Send JMS Text Message using Topic
    Create Producer Topic    RobotTopic4
    Create Consumer Topic   RobotTopic4
    Send Message    Hello from Robot Framework
    Receive    ==    Hello from Robot Framework


Test AssertionEngine With Receive
    Create Producer    RQ1
    Create Consumer    RQ1
    Send Message    Test
    Receive
    Send Message    Test
    Receive    timeout=500
    Send Message    Test
    Receive    ==    Test   timeout=500
    Send Message    Test
    Receive    ==    Test


Assert Response
    Create Producer    AR1
    Create Consumer    AR1
    Send    Hello123
    Receive
    Get Text    ==    Hello123
    Get Text    contains    123    
    

Send JMS Messages And Assert with AssertionEngine
    Create Producer    RQ4
    Create Consumer    RQ4
    Send Message    Test
    Receive
    Send Message    Test
    Receive    timeout=500
    Send Message    Test
    Receive    ==    Test    timeout=1000   
    Send Message    Test
    Receive    !=    Test1
    Send Message    Test
    Run Keyword And Expect Error      Received Message 'Test' (str) should be 'Test123' (str)     Receive    ==    Test123 
    
Send And Receive Messages via Queues

    Send Message To Queue    MyRobotQueue1    Hey There
    ${message}    Receive Message From Queue    MyRobotQueue1    ==    Hey There
    Send Message To Queue    MyRobotQueue1    Hey There
    ${message}    Receive Message From Queue    MyRobotQueue1
    Send Message To Queue    MyRobotQueue1    Hey There
    ${message}    Receive Message From Queue    MyRobotQueue1
    Send Message To Queue    MyRobotQueue1    Hey There
    ${message}    Receive Message From Queue    MyRobotQueue1
    
Mass Sending And Receiving Of Messages via Producer And Consumer Queue
    ${producer}    Create Producer    MassTest
    ${consumer}    Create Consumer    MassTest
    FOR  ${i}    IN RANGE    1000
        Send Message To Producer    ${producer}    Test${i}
    END

    FOR  ${i}    IN RANGE    1000
        ${message}    Receive Message From Consumer    ${consumer}
        Log    ${message}
    END

Mass Sending And Receiving Of Messages via Producer And Consumer Topic
    ${producer}    Create Producer Topic   MassTestTopic
    ${consumer}    Create Consumer Topic   MassTestTopic
    FOR  ${i}    IN RANGE    1000
        Send Message    message=Test${i}    producer=${producer}
    END

    FOR  ${i}    IN RANGE    1000
        ${message}    Receive Message    consumer=${consumer}
        Log    ${message}
    END

Mass Sending And Receiving Of Messages via Queues   
    FOR  ${i}    IN RANGE    1000
        Send Message To Queue    MassTestQueue    Test${i}
    END
    FOR  ${i}    IN RANGE    1000
        ${message}    Receive Message From Queue    MassTestQueue
        Log    ${message}
    END

Mass Sending Of Messages via Queue And Clear   
    FOR  ${i}    IN RANGE    1000
        Send Message To Queue    MassTestQueueClear    Test${i}
    END
    Clear Queue    MassTestQueueClear

Mass Sending Of Messages via Queue Receive ALl in List
    FOR  ${i}    IN RANGE    1000
        Send Message To Queue    MassTestQueueClear    Test${i}
    END
    ${messages}    Receive ALl Messages From Queue    MassTestQueueClear
    Log    ${messages}

Mass Sending Of Messages via Topic Receive ALl in List
    Create Consumer Topic   MassTestTopicClear
    FOR  ${i}    IN RANGE    1000
        Send Message To Topic    MassTestTopicClear    Test${i}
    END
    ${messages}    Receive ALl Messages From Topic    MassTestTopicClear
    Log    ${messages}

Send And Receive JMS Bytes Message using Topic
    Create Producer Topic   RobotTopic1
    Create Consumer Topic   RobotTopic1
    ${message}    Convert to Bytes  01 02 03 04  hex
    Send Message   ${message}
    Create Consumer Topic    RobotTopic1
    ${result}    Convert To Bytes  01 02 03 04  hex
    Receive Message   ==    ${result}
