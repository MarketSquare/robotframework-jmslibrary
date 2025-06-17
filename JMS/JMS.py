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
        self.jms_message = None
        self.last_received_message = None
        self.producers = {}
        self.consumers = {}
        self.queues = {}
        self.topics = {}
        if self.type == "activemq":
            import org.apache.activemq.command.ActiveMQTextMessage as TextMessage
            import org.apache.activemq.command.ActiveMQBytesMessage as BytesMessage
            try:
                self._get_activemq_connection_factory_with_hashtable()
            except:
                self._get_activemq_connection_factory()
        elif self.type == "weblogic":
            import weblogic.jms.common.TextMessageImpl as TextMessage
            import weblogic.jms.common.BytesMessageImpl as BytesMessage
            self._get_weblogic_connection_factory_with_environment()
        else:
            raise Exception("Unknown JMS type")
        self.TextMessage = TextMessage
        self.BytesMessage = BytesMessage

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
        try:
            from javax.jms import Session
        except ImportError:
            from jakarta.jms import Session
        self.connection = self.connectionFactory.createConnection()
        self.session = self.connection.createSession(
            False, Session.AUTO_ACKNOWLEDGE
        )


    def _create_activemq_connection(self):
        try:
            from javax.jms import Session
        except ImportError:
            from jakarta.jms import Session
        if self.username is not None and self.password is not None:
            self.connection = self.connectionFactory.createConnection(
                self.username, self.password
            )
        else:
            self.connection = self.connectionFactory.createConnection()
        self.session = self.connection.createSession(
            False, Session.AUTO_ACKNOWLEDGE
        )

    # def _end_suite(selfself, data, result):
    #     jpype.shutdownJVM()

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

    @keyword
    def create_producer_topic(self, topic: str):
        """
        Create producer for topic ``topic``.
        Producer will be returned and also set as default producer for this instance.

        | =Arguments= | =Description= |
        | ``topic`` | Topic for which the producer is created |
        """
        self.start_connection()
        # Check if producer already exists in self.producers dict with key queue
        if topic in self.producers:
            self.producer = self.producers[topic]
            return self.producers[topic]
        else:
            destination = self._get_topic(topic)
            producer = self.session.createProducer(destination)
            self.producers[topic] = producer
            self.producer = producer
            return producer

    @keyword
    def create_producer_queue(self, queue: str):
        """
        Create producer for queue ``queue``.
        Producer will be returned and also set as default producer for this instance.

        | =Arguments= | =Description= |
        | ``queue`` | Queue for which the producer is created |
        """
        self.start_connection()
        # Check if producer already exists in self.producers dict with key queue
        if queue in self.producers:
            self.producer = self.producers[queue]
            return self.producers[queue]
        else:
            destination = self._get_queue(queue)
            producer = self.session.createProducer(destination)
            self.producers[queue] = producer
            self.producer = producer
            return producer

    @keyword
    def create_producer(self, name: str, createTopic=False):
        """
        *DEPRECATED* Use keyword `Create Producer Topic` or `Create Producer Queue` instead.

        Create producer for ``name``.
        Producer will be returned and also set as default producer for this instance.

        | =Arguments= | =Description= |
        | ``name`` | Name of the queue or topic for which the producer is created |
        """
        if createTopic:
            return self.create_producer_topic(name)
        else:
            return self.create_producer_queue(name)

    @keyword
    def create_consumer_topic(self, topic: str):
        """
        Create consumer for ``topic``.
        Consumer will be returned and also set as default consumer for this instance.

        | =Arguments= | =Description= |
        | ``topic`` | Topic for which the consumer is created |

        Example:
        | Create Consumer Topic | MyTopic |
        | Send Message To Topic | MyTopic | Hello World |
        | Receive Message | == | Hello World |

        """
        self.start_connection()
        # Check if consumer already exists in self.consumers dict with key queue
        if topic in self.consumers:
            self.consumer = self.consumers[topic]
            return self.consumers[topic]
        else:
            destination = self._get_topic(topic)
            consumer = self.session.createConsumer(destination)
            self.consumers[topic] = consumer
            self.consumer = consumer
            return consumer

    @keyword
    def create_consumer_queue(self, queue: str):
        """
        Create consumer for ``queue``.
        Consumer will be returned and also set as default consumer for this instance.

        | =Arguments= | =Description= |
        | ``queue`` | Queue for which the consumer is created |

        Example:
        | Create Consumer Queue | MyQueue |
        | Send Message To Queue | MyQueue | Hello World |
        | Receive Message | == | Hello World |


        """
        self.start_connection()
        # Check if consumer already exists in self.consumers dict with key queue
        if queue in self.consumers:
            self.consumer = self.consumers[queue]
            return self.consumers[queue]
        else:
            destination = self._get_queue(queue)
            consumer = self.session.createConsumer(destination)
            self.consumers[queue] = consumer
            self.consumer = consumer
            return consumer

    @keyword
    def create_consumer(self, name: str, createTopic=False):
        """
        *DEPRECATED* Use keyword `Create Consumer Topic` or `Create Consumer Queue` instead.

        Create consumer for ``name``.
        Consumer will be returned and also set as default consumer for this instance.

        | =Arguments= | =Description= |
        | ``name`` | Name of the queue for which the consumer is created |

        Example:
        | Create Consumer | MyQueue |
        | Send Message To Queue | MyQueue | Hello World |
        | Receive Message | == | Hello World |


        """
        if createTopic:
            return self.create_consumer_topic(name)
        else:
            return self.create_consumer_queue(name)


    @keyword
    def create_message(self, message: str):
        """
        *DEPRECATED* Use keyword `Create Text Message` instead.

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
        self.create_text_message(message)

    @keyword
    def create_text_message(self, message: str):
        """
        Creates a JMS text message from ``message`` and sets it as default message for this instance.
        After calling this keyword, ``Send Message`` keyword can be used without passing message.

        The JMS message object is returned and also set as default message for this instance.

        | =Arguments= | =Description= |
        | ``message`` | Text of the message |

        Example:
        | Create Message | Hello World |
        | Create Producer Queue | MyQueue |
        | Send Message | |
        | Receive Message From Queue | MyQueue | == | Hello World |

        """
        text_message = self.TextMessage()
        text_message.setText(message)
        self.jms_message = text_message
        return text_message

    @keyword
    def create_bytes_message(self, message: bytes):
        """
        Creates a JMS bytes message from ``message`` and sets it as default message for this instance.
        After calling this keyword, ``Send`` keyword can be used without passing message.

        The JMS message object is returned and also set as default message for this instance.

        | =Arguments= | =Description= |
        | ``message`` | Bytes message |

        Example:
        | Create Bytes Message | Hello World |
        | Create Producer Queue| MyQueue |
        | Send Message | |
        | Receive Message From Queue | MyQueue | == | Hello World |

        """
        bytes_message = self.BytesMessage()
        bytes_message.writeBytes(message)
        self.jms_message = bytes_message
        return bytes_message

    @keyword
    def receive(
        self,
        assertion_operator: Optional[AssertionOperator] = None,
        assertion_expected: Optional[Any] = None,
        message: Optional[str] = None,
        timeout: Optional[int]=None,
        consumer: Optional[Any] = None,
    ) -> Any:
        """
        *DEPRECATED* Use keyword `Receive Message` instead.

        Returns text of JMS message from consumer and verifies assertion.

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
        return self.receive_message(assertion_operator, assertion_expected, message, timeout, consumer)

    @keyword
    def receive_message(
        self,
        assertion_operator: Optional[AssertionOperator] = None,
        assertion_expected: Optional[Any] = None,
        message: Optional[str] = None,
        timeout: Optional[int]=None,
        consumer: Optional[Any] = None,
    ) -> Any:
        """Returns content (text or binary) of JMS message from consumer and verifies assertion.

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
    def receive_message_from_consumer(
            self,
            consumer,
            assertion_operator: Optional[AssertionOperator] = None,
            assertion_expected: Optional[Any] = None,
            message: Optional[str] = None,
            timeout: Optional[int]=None,
    ) -> Any:
        """
        *DEPRECATED* Use keyword `Receive Message` instead.
        """
        value = self._receive_message_from_jms(consumer=consumer, timeout = timeout)
        formatter = self.keyword_formatters.get(self.receive_message_from_consumer)
        return verify_assertion(
        value, assertion_operator, assertion_expected, "Received Message", message, formatter
            )

    @keyword
    def receive_message_from_queue(
        self,
        queue: str,
        assertion_operator: Optional[AssertionOperator] = None,
        assertion_expected: Optional[Any] = None,
        message: Optional[str] = None,
        timeout: Optional[int] = None,
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
        consumer = self.create_consumer_queue(queue)
        return self.receive_message(assertion_operator, assertion_expected, message, timeout, consumer)

    @keyword
    def receive_message_from_topic(
            self,
            topic: str,
            assertion_operator: Optional[AssertionOperator] = None,
            assertion_expected: Optional[Any] = None,
            message: Optional[str] = None,
            timeout: Optional[int] = None,
    ) -> Any:
        """
        Receive message from queue and verify assertion.

        | =Arguments= | =Description= |
        | ``topic`` | Topic to receive message from |
        | ``assertion_operator`` | See `Assertions` for further details. Defaults to None. |
        | ``assertion_expected`` | Expected value for the state |
        | ``message`` | overrides the default error message for assertion. |
        | ``timeout`` | Timeout in milliseconds. Defaults to 2000. |

        Example:
        | Send Message To Topic | MyTopic | Hello World |
        | Receive Message From Topic | MyTopic | == | Hello World |

        """
        consumer = self.create_consumer_topic(topic)
        return self.receive_message(assertion_operator, assertion_expected, message, timeout, consumer)

    @keyword
    def send(self, message=None):
        """
        *DEPRECATED* Use keyword `Send Message` instead.

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
        self.send_message(message)

    @keyword
    def send_message(self, message=None, producer: Optional[Any] = None,):
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
        jms_message = None
        if producer is None:
            producer = self.producer
        if message is not None:
            if isinstance(message, str):
                jms_message = self.create_text_message(message)
            elif isinstance(message, bytes):
                jms_message = self.create_bytes_message(message)
            else:
                jms_message = message
        elif self.jms_message is not None:
            jms_message = self.jms_message
        if jms_message is None:
            raise Exception("No message to send")
        producer.send(jms_message)
        print("Message sent successfully!")

    @keyword
    def send_message_to_producer(self, producer, message=None):
        """
        *DEPRECATED* Use keyword `Send Message` instead.

        Send message to producer.
        
        | =Arguments= | =Description= |
        | ``producer`` | Producer to send message to |
        | ``message`` | Text of the message or message object |

        Example:
        | ${producer}= | Create Producer | MyQueue |
        | Send Message To Producer | ${producer} | Hello World |

        """
        self.send_message(message, producer=producer)

    @keyword
    def send_message_to_queue(self, queue: str, message=None):
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
        producer = self.create_producer_queue(queue)
        self.send_message(message, producer=producer)

    @keyword
    def send_message_to_topic(self, topic: str, message=None):
        """
        Send message to topic.

        | =Arguments= | =Description= |
        | ``topic`` | Topic to send message to |
        | ``message`` | Text of the message or message object |

        Example:
        | Send Message To Topic | MyTopic | Hello World |
        | ${message}= | Create Message | Hello There |
        | Send Message To Topic | MyTopic | ${message} |

        """
        producer = self.create_producer_topic(topic)
        self.send_message(message, producer=producer)

    @keyword
    def clear_queue(self, queue: str):
        """
        Clear all messages from queue.

        | =Arguments= | =Description= |
        | ``queue`` | Queue to clear |

        Example:
        | Send Message To Queue | MyQueue | Hello World |
        | Clear Queue | MyQueue |
        """

        consumer = self.create_consumer_queue(queue)
        while True:
            jms_message = consumer.receive(100)
            if jms_message is None:
                break

    @keyword
    def clear_topic(self, topic: str):
        """
        Clear all messages from topic.

        | =Arguments= | =Description= |
        | ``topic`` | Topic to clear |

        Example:
        | Send Message To Queue | MyTopic | Hello World |
        | Clear Topic | MyTopic |
        """

        consumer = self.create_consumer_topic(topic)
        while True:
            jms_message = consumer.receive(100)
            if jms_message is None:
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
        consumer = self.create_consumer_queue(queue)
        messages = []
        if timeout is None:
            timeout = self.timeout
        while True:
            message = consumer.receive(timeout)
            if message is None:
                break
            messages.append(message.getText())
        return messages

    @keyword
    def receive_all_messages_from_topic(self, topic, timeout=None):
        """
        Receive all messages from topic and return them as list.

        | =Arguments= | =Description= |
        | ``topic`` | Topic to receive messages from |
        | ``timeout`` | Timeout in milliseconds. Defaults to 2000. |

        Example:
        | Send Message To Topic | MyTopic | Hello World |
        | Send Message To Topic | MyTopic | Hello Again |
        | ${messages}= | Receive All Messages From Topic | MyTopic |
        | Should Be Equal As Strings | ${messages}[0] | Hello World |
        | Should Be Equal As Strings | ${messages}[1] | Hello Again |

        """
        consumer = self.create_consumer_topic(topic)
        messages = []
        if timeout is None:
            timeout = self.timeout
        while True:
            message = consumer.receive(timeout)
            if message is None:
                break
            messages.append(message.getText())
        return messages

    def _get_queue(self, name: str):
        if name in self.queues:
            return self.queues[name]
        else:
            if self.type == "weblogic":
                self.queues[name] = self.jndiContext.lookup(name)
            else:
                self.queues[name] = self.session.createQueue(name)
            return self.queues[name]

    def _get_topic(self, name: str):
        if name in self.topics:
            return self.topics[name]
        else:
            self.topics[name] = self.session.createTopic(name)
            return self.topics[name]

    def _close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def get_text(
            self,
            assertion_operator: Optional[AssertionOperator] = None,
            assertion_expected: Optional[Any] = None,
            message: Optional[str] = None,
            ) -> Any:
        """
        Get text from last received jms message and verify assertion.

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

    @keyword
    def get_properties_from_message(self, jms_message = None):
        """

        Get properties from ``jms_message``.

        | =Arguments= | =Description= |
        | ``jms_message`` | JMS message to get property from |

        Example:
        | Send Message To Queue | MyQueue | Hello World |
        | ${message}= | Receive Message From Queue | MyQueue |
        | &{dict}= Get Properties From Message | ${message}

        """
        props = {}
        if jms_message is not None:
            props = dict(jms_message.getProperties())
        elif self.last_received_message is not None:
            props = dict(self.last_received_message.getProperties())
        for key, value in props.items():
            props[key] = str(value)
        return props

    @keyword
    def get_property_from_message(self, name: str,
                                  assertion_operator: Optional[AssertionOperator] = None,
                                  assertion_expected: Optional[Any] = None,
                                  message: Optional[str] = None,
                                  jms_message = None,
                                  ) -> Any:
        """

        get property from ``jms_message``.
        If jms_message is passed, it will be used. Otherwise, last received message will be used.

        | =Arguments= | =Description= |
        | ``name`` | Name of the property |
        | ``assertion_operator`` | See `Assertions` for further details. Defaults to None. |
        | ``assertion_expected`` | Expected value for the state |
        | ``message`` | overrides the default error message for assertion. |
        | ``jms_message`` | JMS message to set property |

        Example:
        | ${message}= | Create Text Message | MyQueue |
        | Get Property From Message | REPLY_TO | ${message}

        """
        value = None
        if jms_message is not None:
            value = jms_message.getProperty(name)
        elif self.jms_message is not None:
            value = self.jms_message.getProperty(name)
        formatter = self.keyword_formatters.get(self.get_property_from_message)
        return verify_assertion(
        value, assertion_operator, assertion_expected, "Received Property", message, formatter
            )


    @keyword
    def set_property_to_message(self, name: str, value = None, jms_message = None):
        """

        Set property to ``jms_message``.
        If jms_message is passed, it will be used. Otherwise, message from ``Create Message`` will be used.

        | =Arguments= | =Description= |
        | ``name`` | Name of the property |
        | ``value`` | Value of the property |
        | ``jms_message`` | JMS message to set property |

        Example:
        | ${message}= | Create Text Message | MyQueue |
        | Set Property to Message | REPLY_TO | Test | ${message}

        """
        if jms_message is not None:
            jms_message.setProperty(name, value)
            return jms_message
        elif self.jms_message is not None:
            self.jms_message.setProperty(name, value)
            return self.jms_message

    def _receive_message_from_jms(self, consumer = None, timeout: int = None):
        if consumer is None:
            raise Exception("You need to pass a consumer")
        if timeout is None:
            timeout = self.timeout
        received_message = consumer.receive(timeout)
        self.last_received_message = received_message
        if isinstance(received_message, self.TextMessage):
            return str(received_message.getText())
        elif isinstance(received_message,self.BytesMessage):
            received_bytes = bytearray()
            length = received_message.getBodyLength()
            while length > 0:
                received_bytes.append(received_message.readUnsignedByte())
                length -= 1
            return received_bytes
        else:
            return AssertionError("No message received")

    @keyword
    def set_timeout(self, timeout):
        """
        Set global timeout for receive message
        """
        self.timeout = timeout