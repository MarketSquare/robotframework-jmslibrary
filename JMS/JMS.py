import jpype
import jpype.imports
from robot.api.deco import keyword, library
import logging
from typing import Any, List, Optional, Union
from assertionengine import (
    AssertionOperator,
    bool_verify_assertion,
    dict_verify_assertion,
    flag_verify_assertion,
    float_str_verify_assertion,
    int_dict_verify_assertion,
    list_verify_assertion,
    verify_assertion,
    Formatter,
)
classpath="jars/*"
jpype.startJVM(classpath=[classpath])


class JMS(object):
    ROBOT_LISTENER_API_VERSION = 3


    def __init__(
        self,
        type="activemq",
        classpath="jars/*",
        server="localhost",
        port=61616,
        username=None,
        password=None,
        connection_factory="ConnectionFactory",
        timeout = 2000,
    ) -> None:
        """JMS library for Robot Framework
        
        | =Arguments= | =Description= |
        | ``type`` | Type of JMS server. Currently only ``activemq`` and ``weblogic`` are supported. Defaults to ``activemq`` |
        | ``classpath`` | Classpath to JMS jars. Defaults to ``jars/*`` |
        | ``server`` | JMS server address. Defaults to ``localhost`` |
        | ``port`` | JMS server port. Defaults to ``61616`` |
        | ``username`` | Username for JMS server. Defaults to ``None`` |
        | ``password`` | Password for JMS server. Defaults to ``None`` |
        | ``connection_factory`` | Connection factory name. Defaults to ``ConnectionFactory`` |
        | ``timeout`` | Timeout in milliseconds. Defaults to ``2000`` |
        
        Connection URL for ActiveMQ is ``tcp://<server>:<port>``
        Connection URL for Weblogic is ``t3://<server>:<port>``
        """
        self.keyword_formatters = {}
        if not jpype.isJVMStarted():
            jpype.startJVM(classpath=[classpath])
        self.ROBOT_LIBRARY_LISTENER = self
        self.type = type
        self.classpath = classpath
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.connection_factory = connection_factory
        self.connection = None
        self.producer = None
        self.consumer = None
        self.message = None
        self.last_received_message = None
        self.producers = {}
        self.consumers = {}
        self.queues = {}
        if self.type == "activemq":
            import org.apache.activemq.command.ActiveMQTextMessage as TextMessage
            try:                
                self._get_activemq_connection_factory_with_hashtable()
            except:
                self._get_activemq_connection_factory()
        elif self.type == "weblogic":
            import weblogic.jms.common.TextMessageImpl as TextMessage
            self._get_weblogic_connection_factory_with_environment()
        else:
            raise Exception("Unknown JMS type")
        self.TextMessage = TextMessage

    def _get_weblogic_connection_factory_with_hashtable(self):
        #Create a Context object
        from javax.naming import Context
        from javax.naming import InitialContext
        
        #Create a Java Hashtable instance
        from java.util import Hashtable

        properties = Hashtable()
        properties.put(Context.INITIAL_CONTEXT_FACTORY, "weblogic.jndi.WLInitialContextFactory")
        properties.put(Context.PROVIDER_URL, "t3://{}:{}".format(self.server, self.port))
        properties.put(Context.SECURITY_PRINCIPAL, self.username)
        properties.put(Context.SECURITY_CREDENTIALS, self.password)

        self.jndiContext = InitialContext(properties)
        self.connectionFactory = self.jndiContext.lookup(self.connection_factory)
    
    def _get_weblogic_connection_factory_with_environment(self):
         #Create a Context object
        from javax.naming import Context
        from javax.naming import InitialContext
        from weblogic.jndi import Environment
        env = Environment()
        env.setProviderUrl("t3://{}:{}".format(self.server, self.port))
        env.setSecurityPrincipal(self.username)
        env.setSecurityCredentials(self.password)
        env.setConnectionTimeout(10000)
        env.setResponseReadTimeout(15000)
        self.jndiContext = env.getInitialContext()
        self.connectionFactory = self.jndiContext.lookup(self.connection_factory)


    def _get_activemq_connection_factory(self):
        from org.apache.activemq import ActiveMQConnectionFactory as ConnectionFactory
        # Create connection factory
        self.connectionFactory = self.ConnectionFactory(
            "tcp://{}:{}".format(self.server, self.port)
        )
    
    def _get_activemq_connection_factory_with_hashtable(self):

        from javax.naming import Context
        from javax.naming import InitialContext

        #Create a Java Hashtable instance
        from java.util import Hashtable
        properties = Hashtable()
        properties.put(Context.INITIAL_CONTEXT_FACTORY, "org.apache.activemq.jndi.ActiveMQInitialContextFactory")
        properties.put(Context.PROVIDER_URL, "tcp://{}:{}".format(self.server, self.port))
        if self.username is not None and self.password is not None:
            properties.put(Context.SECURITY_PRINCIPAL, self.username)
            properties.put(Context.SECURITY_CREDENTIALS, self.password)

        self.jndiContext = InitialContext(properties)
        self.connectionFactory = self.jndiContext.lookup(self.connection_factory)

    def _create_weblogic_connection(self):
        from javax.jms import Session
        self.connection = self.connectionFactory.createConnection()
        self.session = self.connection.createSession(
            False, Session.AUTO_ACKNOWLEDGE
        )


    def _create_activemq_connection(self):
        from javax.jms import Session
        if self.username is not None and self.password is not None:
            self.connection = self.connectionFactory.createConnection(
                self.username, self.password
            )
        else:
            self.connection = self.connectionFactory.createConnection()
        self.session = self.connection.createSession(
            False, Session.AUTO_ACKNOWLEDGE
        )

    @keyword
    def create_connection(self):
        """
        Create connection to JMS server
        """
        if self.connection is not None:
            print("Connection already created")
            return
        if self.type == "weblogic":
            self._create_weblogic_connection()
        else:
            self._create_activemq_connection()

    @keyword
    def start_connection(self):
        """
        Start connection to JMS server.
        If connection is already started, nothing happens
        """
        if self.connection is None:
            self.create_connection()
        self.connection.start()

    @keyword
    def stop_connection(self):
        """
        Stop connection to JMS server.
        """
        self.connection.stop()

    @keyword
    def close_connection(self):
        """
        Close connection to JMS server.
        Shutdown JVM.
        """
        # Close connection and clean up
        self.connection.close()
        self.connection = None
        jpype.shutdownJVM()

    @keyword
    def create_producer(self, queue: str):
        """
        Create producer for ``queue``.
        Producer will be returned and also set as default producer for this instance.

        | =Arguments= | =Description= |
        | ``queue`` | Name of the queue for which the producer is created |
        """
        self.start_connection()
        # Check if producer already exists in self.producers dict with key queue
        if queue in self.producers:
            self.producer = self.producers[queue]
            return self.producers[queue]
        else:
            # Create queue (replace with topic if needed)
            destination = self.get_queue(queue)
            producer = self.session.createProducer(destination)
            self.producers[queue] = producer
            self.producer = producer
            return producer

    @keyword
    def create_consumer(self, queue):
        """
        Create consumer for ``queue``.
        Consumer will be returned and also set as default consumer for this instance.

        | =Arguments= | =Description= |
        | ``queue`` | Name of the queue for which the consumer is created |

        Example:
        | Create Consumer | MyQueue |
        | Send Message To Queue | MyQueue | Hello World |
        | Receive Message | == | Hello World |


        """
        self.start_connection()
        # Check if consumer already exists in self.consumers dict with key queue
        if queue in self.consumers:
            self.consumer = self.consumers[queue]
            return self.consumers[queue]
        else:
            # Create queue (replace with topic if needed)
            destination = self.get_queue(queue)
            consumer = self.session.createConsumer(destination)
            self.consumers[queue] = consumer
            self.consumer = consumer
            return consumer

    @keyword
    def create_message(self, message: str):
        """
        Creates a message from ``message`` and sets it as default message for this instance.
        After calling this keyword, ``Send`` keyword can be used without passing message.

        The message is object returned and also set as default message for this instance.

        | =Arguments= | =Description= |
        | ``message`` | Text of the message |

        Example:
        | Create Message | Hello World |
        | Create Producer | MyQueue |
        | Send | |
        | Receive Message From Queue | MyQueue | == | Hello World |

        """
        text_message = self.TextMessage()
        text_message.setText(message)
        self.message = text_message
        return text_message

    @keyword
    def send(self, message=None):
        """
        Send message to default producer.
        If message is passed, it will be sent. Otherwise, message from ``Create Message`` will be sent.

        | =Arguments= | =Description= |
        | ``message`` | Text of the message or message object|

        Example:
        | Create Message | Hello World |
        | Create Producer | MyQueue |
        | Send | |
        | Receive Message From Queue | MyQueue | == | Hello World |
        | ${message}= | Create Message | Hello There |
        | Send | ${message} |
        | Receive Message From Queue | MyQueue | == | Hello There |
        """
        if message is not None:
            if isinstance(message, str):
                text_message = self.TextMessage()
                text_message.setText(message)
                self.message = text_message
            else:
                text_message = message
        elif self.message is not None:
            text_message = self.message
        else:
            raise Exception("No message to send")
        if self.producer is None:
            raise Exception("Producer not created")
        self.producer.send(text_message)
        print("Message sent successfully!")


    @keyword
    def receive(
        self,
        assertion_operator: Optional[AssertionOperator] = None,
        assertion_expected: Optional[Any] = None,
        message: Optional[str] = None,
        timeout: Optional[int]=None,
        consumer: Optional[Any] = None,
    ) -> Any:
        """Returns text of JMS message from consumer and verifies assertion.

        | =Arguments= | =Description= |
        | ``assertion_operator`` | See `Assertions` for further details. Defaults to None. |
        | ``assertion_expected`` | Expected value for the state |
        | ``message`` | overrides the default error message for assertion. |
        | ``timeout`` | Timeout in milliseconds. Defaults to 2000. |
        | ``consumer`` | Consumer to receive message from. If not passed, a consumer needs to be created before using ``Create Consumer`` |

        Example:
        | Create Consumer | MyQueue |
        | Send Message To Queue | MyQueue | Hello World |
        | ${message}= | Receive Message | == | Hello World |
        | Should Be Equal | ${message} | Hello World |

        """

        if consumer is None:
            consumer = self.consumer

        value = self._receive_message_from_jms(consumer=consumer, timeout = timeout)
        formatter = self.keyword_formatters.get(self.receive)
        return verify_assertion(
                value, assertion_operator, assertion_expected, "Received Message", message, formatter
            )

    @keyword
    def receive_message(
        self,
        assertion_operator: Optional[AssertionOperator] = None,
        assertion_expected: Optional[Any] = None,
        message: Optional[str] = None,
        timeout: Optional[int]=None,
        consumer: Optional[Any] = None,
    ) -> Any:
        """Returns text of JMS message from consumer and verifies assertion.

        | =Arguments= | =Description= |
        | ``assertion_operator`` | See `Assertions` for further details. Defaults to None. |
        | ``assertion_expected`` | Expected value for the state |
        | ``message`` | overrides the default error message for assertion. |
        | ``timeout`` | Timeout in milliseconds. Defaults to 2000. |
        | ``consumer`` | Consumer to receive message from. If not passed, a consumer needs to be created before using ``Create Consumer`` |

        Example:
        | Create Consumer | MyQueue |
        | Send Message To Queue | MyQueue | Hello World |
        | ${message}= | Receive Message | == | Hello World |
        | Should Be Equal | ${message} | Hello World |

        """
        if consumer is None:
            consumer = self.consumer
        value = self._receive_message_from_jms(consumer=consumer, timeout=timeout)
        formatter = self.keyword_formatters.get(self.receive_message)
        return verify_assertion(
                value, assertion_operator, assertion_expected, "Received Message", message, formatter
            )

    @keyword
    def send_message(self, message=None):
        """
        Send message to default producer.
        If message is passed, it will be sent. Otherwise, message from ``Create Message`` will be sent.

        | =Arguments= | =Description= |
        | ``message`` | Text of the message or message object |

        Example:
        | Create Message | Hello World |
        | Create Producer | MyQueue |
        | Send Message| |
        | Receive Message From Queue | MyQueue | == | Hello World |
        | ${message}= | Create Message | Hello There |
        | Send Message | ${message} |
        | Receive Message From Queue | MyQueue | == | Hello There |
        | Send Message | Hello Again |
        | Receive Message From Queue | MyQueue | == | Hello Again |

        """
        if message is not None:
            if isinstance(message, str):
                text_message = self.TextMessage()
                text_message.setText(message)
                self.message = text_message
            else:
                text_message = message
        elif self.message is not None:
            text_message = self.message
        else:
            raise Exception("No message to send")
        if self.producer is None:
            raise Exception("Producer not created")
        self.producer.send(text_message)
        print("Message sent successfully!")

    @keyword
    def send_message_to_producer(self, producer, message):
        """
        Send message to producer.
        
        | =Arguments= | =Description= |
        | ``producer`` | Producer to send message to |
        | ``message`` | Text of the message or message object |

        Example:
        | ${producer}= | Create Producer | MyQueue |
        | Send Message To Producer | ${producer} | Hello World |

        """
        if isinstance(message, str):
            text_message = self.TextMessage()
            text_message.setText(message)
        else:
            text_message = message
        producer.send(text_message)
        print("Message sent successfully!")

    @keyword
    def send_message_to_queue(self, queue, message):
        """
        Send message to queue.

        | =Arguments= | =Description= |
        | ``queue`` | Queue to send message to |
        | ``message`` | Text of the message or message object |

        Example:
        | Send Message To Queue | MyQueue | Hello World |
        | ${message}= | Create Message | Hello There |
        | Send Message To Queue | MyQueue | ${message} |

        """

        if isinstance(message, str):
            text_message = self.TextMessage()
            text_message.setText(message)
        else:
            text_message = message    
        producer = self.create_producer(queue)
        producer.send(text_message)
        print("Message sent successfully!")

    @keyword
    def receive_message_from_consumer(
        self,
        consumer, 
        assertion_operator: Optional[AssertionOperator] = None,
        assertion_expected: Optional[Any] = None,
        message: Optional[str] = None,
        timeout: Optional[int]=None,
    ) -> Any:
        value = self._receive_message_from_jms(consumer=consumer, timeout = timeout)
        formatter = self.keyword_formatters.get(self.receive_message_from_consumer)
        return verify_assertion(
                value, assertion_operator, assertion_expected, "Received Message", message, formatter
            )

    @keyword
    def receive_message_from_queue(
        self,
        queue, 
        assertion_operator: Optional[AssertionOperator] = None,
        assertion_expected: Optional[Any] = None,
        message: Optional[str] = None,
        timeout: Optional[int]=None,
    ) -> Any:
        """
        Receive message from queue and verify assertion.

        | =Arguments= | =Description= |
        | ``queue`` | Queue to receive message from |
        | ``assertion_operator`` | See `Assertions` for further details. Defaults to None. |
        | ``assertion_expected`` | Expected value for the state |
        | ``message`` | overrides the default error message for assertion. |
        | ``timeout`` | Timeout in milliseconds. Defaults to 2000. |

        Example:
        | Send Message To Queue | MyQueue | Hello World |
        | Receive Message From Queue | MyQueue | == | Hello World |
        
        """
        value = self._receive_message_from_jms(queue=queue, timeout=timeout)
        formatter = self.keyword_formatters.get(self.receive_message_from_queue)
        return verify_assertion(
                value, assertion_operator, assertion_expected, "Received Message", message, formatter
            )

    @keyword
    def clear_queue(self, queue):
        """
        Clear all messages from queue.

        | =Arguments= | =Description= |
        | ``queue`` | Queue to clear |

        Example:
        | Send Message To Queue | MyQueue | Hello World |
        | Clear Queue | MyQueue |
        """

        consumer = self.create_consumer(queue)
        while True:
            message = consumer.receive(100)
            if message is None:
                break

    @keyword
    def receive_all_messages_from_queue(self, queue, timeout=None):
        """
        Receive all messages from queue and return them as list.

        | =Arguments= | =Description= |
        | ``queue`` | Queue to receive messages from |
        | ``timeout`` | Timeout in milliseconds. Defaults to 2000. |

        Example:
        | Send Message To Queue | MyQueue | Hello World |
        | Send Message To Queue | MyQueue | Hello Again |
        | ${messages}= | Receive All Messages From Queue | MyQueue |
        | Should Be Equal As Strings | ${messages}[0] | Hello World |
        | Should Be Equal As Strings | ${messages}[1] | Hello Again |

        """
        consumer = self.create_consumer(queue)
        messages = []
        if timeout is None:
            timeout = self.timeout
        while True:
            message = consumer.receive(timeout)
            if message is None:
                break
            messages.append(message.getText())
        return messages

    def get_queue(self, queue):
        if queue in self.queues:
            return self.queues[queue]
        else:
            if self.type == "weblogic":
                self.queues[queue] = self.jndiContext.lookup(queue)
            else:
                self.queues[queue] = self.session.createQueue(queue)
            return self.queues[queue]

    def get_topic(self, topic):
        return self.session.createTopic(topic)

    def _close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            # jpype.shutdownJVM()

    def get_text(
            self,
            assertion_operator: Optional[AssertionOperator] = None,
            assertion_expected: Optional[Any] = None,
            message: Optional[str] = None,
            ) -> Any:
        """
        Get text from last received message and verify assertion.

        | =Arguments= | =Description= |
        | ``assertion_operator`` | See `Assertions` for further details. Defaults to None. |
        | ``assertion_expected`` | Expected value for the state |
        | ``message`` | overrides the default error message for assertion. |

        Example:
        | Send Message To Queue | MyQueue | Hello World |
        | Receive Message From Queue | MyQueue | == | Hello World |
        | Get Text | == | Hello World |
        | ${text}= | Get Text |
        | Should Be Equal | ${text} | Hello World |
        
        """     
        if self.last_received_message is not None:
            value = self.last_received_message.getText()
        else:
            raise Exception("No message to get text from")
        formatter = self.keyword_formatters.get(self.get_text)
        return verify_assertion(
                value, assertion_operator, assertion_expected, "Message Text", message, formatter
            )
        
    def get_text_from_message(
        self, 
        jms_message,
        assertion_operator: Optional[AssertionOperator] = None,
        assertion_expected: Optional[Any] = None,
        message: Optional[str] = None,
        timeout: Optional[int]=None,
        ) -> Any: 
        """

        Get text from ``jms_message`` and verify assertion.

        | =Arguments= | =Description= |
        | ``jms_message`` | JMS message to get text from |
        | ``assertion_operator`` | See `Assertions` for further details. Defaults to None. |
        | ``assertion_expected`` | Expected value for the state |
        | ``message`` | overrides the default error message for assertion. |

        Example:
        | Send Message To Queue | MyQueue | Hello World |
        | ${message}= | Receive Message From Queue | MyQueue |
        | Get Text From Message | ${message} | == | Hello World |
        | ${text}= | Get Text From Message | ${message} |
        | Should Be Equal | ${text} | Hello World |
        
        """
        if jms_message is not None:
            value = jms_message.getText()
        else:
            raise Exception("No message to get text from")
        formatter = self.keyword_formatters.get(self.get_text_from_message)
        return verify_assertion(
                value, assertion_operator, assertion_expected, "Message Text", message, formatter
            )

    
    def _receive_message_from_jms(self, consumer = None, queue: str = None , timeout: int = None):
        if consumer and queue:
            raise Exception("You can only pass either consumer or queue")
        if consumer is None and queue is None:
            raise Exception("You need to pass either consumer or queue")
        if consumer is None:
            consumer = self.create_consumer(queue)
        if timeout is None:
            timeout = self.timeout
        received_message = consumer.receive(timeout)
        self.last_received_message = received_message
        if isinstance(received_message, self.TextMessage):
            return str(received_message.getText())
        elif received_message is None:
            return AssertionError("No message received")
        
    @keyword
    def set_timeout(self, timeout):
        """
        Set global timeout for receive message
        """
        self.timeout = timeout