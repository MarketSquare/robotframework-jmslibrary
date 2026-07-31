*** Settings ***
Library  JMS

Test Teardown    Close Connection

*** Test Cases ***
Send And Receive JMS Text Message using Queue
    Create Producer Queue   RobotQueue1
    Send Message    Hello from Robot Framework
    Create Consumer Queue   RobotQueue1
    Receive Message  ==    Hello from Robot Framework

Send JMS Text Message using Queue
    Create Producer Queue   RobotQueue4
    Send Message    Hello from Robot Framework
    Create Consumer Queue   RobotQueue4
    Receive Message  ==    Hello from Robot Framework

Send And Receive JMS Text Message using Topic
    Create Producer Topic   RobotTopic1
    Create Consumer Topic   RobotTopic1
    Send Message   Hello from Robot Framework
    Receive Text Message   ==    Hello from Robot Framework

Send JMS Text Message using Topic
    Create Producer Topic    RobotTopic4
    Create Consumer Topic   RobotTopic4
    Send Message    Hello from Robot Framework
    Receive Message From Topic   RobotTopic4    ==    Hello from Robot Framework


Test AssertionEngine With Receive
    Create Producer Topic    RQ1
    Create Consumer Topic   RQ1
    Send Message    Test
    Receive Message
    Send Message    Test
    Receive Message  timeout=500
    Send Message    Test
    Receive Message  ==    Test   timeout=500
    Send Message    Test
    Receive Message  ==    Test


Assert Response with Text
    Create Producer Queue   AR1
    Create Consumer Queue    AR1
    Send Message    Hello123
    Receive Message
    Get Text    ==    Hello123
    Get Text    contains    123    

Assert Response with Bytes
    Create Producer Queue   AR2
    Create Consumer Queue    AR2
    ${message_body}    Convert To Bytes    Hello123
    ${expected_body}    Convert To Bytes    Hello123
    ${expected_body_part}    Convert To Bytes    123
    Send Message    ${message_body}
    Receive Message
    Get Bytes    ==    ${expected_body}
    Get Bytes    contains    ${expected_body_part}


Send JMS Messages And Assert with AssertionEngine
    Create Producer Topic    RQ4
    Create Consumer Topic    RQ4
    Send Message    Test
    Receive Message
    Send Message    Test
    Receive Message  timeout=500
    Send Message    Test
    Receive Message  ==    Test    timeout=1000
    Send Message    Test
    Receive Message  !=    Test1
    Send Message    Test
    Run Keyword And Expect Error      Received Message 'Test' (str) should be 'Test123' (str)     Receive Message  ==    Test123
    
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
    ${producer}    Create Producer Queue   MassTest
    ${consumer}    Create Consumer Queue   MassTest
    FOR  ${i}    IN RANGE    1000
        Send Message    producer=${producer}    message=Test${i}
    END

    FOR  ${i}    IN RANGE    1000
        ${message}    Receive Message   consumer=${consumer}
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
    Receive Message From Queue  MassTestQueueClear  ==  ${None}  timeout=5

Mass Sending Of Messages via Topic And Clear
    FOR  ${i}    IN RANGE    1000
        Send Message To Topic    MassTestTopicClear    Test${i}
    END
    Clear Topic    MassTestTopicClear
    Receive Message From Topic  MassTestTopicClear  ==  ${None}  timeout=5

Mass Sending Of Text Messages via Queue Receive All in List
    FOR  ${i}    IN RANGE    1000
        Send Message To Queue    MassTestQueueClear    Test${i}
    END
    ${messages}    Receive ALl Messages From Queue    MassTestQueueClear
    Log    ${messages}

Mass Sending Of Text Messages via Topic Receive All in List
    Create Consumer Topic   MassTestTopicClear
    FOR  ${i}    IN RANGE    1000
            Send Message To Topic    MassTestTopicClear    Test${i}
    END
    ${messages}    Receive ALl Messages From Topic    MassTestTopicClear
    Log    ${messages}

Mass Sending Of Bytes Messages via Queue Receive All in List
    FOR  ${i}    IN RANGE    1000
        ${message}    Convert to Bytes  Test${i}
        Send Message To Queue    MassTestQueueClear    ${message}
    END
    ${messages}    Receive ALl Messages From Queue    MassTestQueueClear
    Log    ${messages}

Mass Sending Of Bytes Messages via Topic Receive All in List
    Create Consumer Topic   MassTestTopicClear
    FOR  ${i}    IN RANGE    1000
        ${message}    Convert to Bytes  Test${i}
            Send Message To Topic    MassTestTopicClear    ${message}
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
    Receive Bytes Message   ==    ${result}

Send and receive JMS Message with property
    Create Producer Topic   RobotTopicProperty
    Create Consumer Topic   RobotTopicProperty
    Create Text Message   Hello from Robot Framework
    Set Property To Message   StringProp    StringValue
    Set Property To Message   IntProp    ${10}
    Send Message
    Receive Message   ==    Hello from Robot Framework
    Get Property From Message   StringProp  ==  StringValue
    Get Property From Message   IntProp  ==  ${10}

Receive JMS Message and get all properties
    Create Producer Topic   RobotTopicProperty
    Create Consumer Topic   RobotTopicProperty
    Create Text Message   Hello from Robot Framework
    Set Property To Message   StringProp    StringValue
    Set Property To Message   IntProp    ${10}
    Send Message
    Receive Message   ==    Hello from Robot Framework
    &{properties} =  Get Properties From Message
    Log Many  &{properties}

