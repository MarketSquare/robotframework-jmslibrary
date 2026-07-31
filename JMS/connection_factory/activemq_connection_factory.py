from JMS.connection_factory.abstract_connection_factory import AbstractConnectionFactory

class ActivemqConnectionFactory(AbstractConnectionFactory):

    def _create_connection(self):
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
        return self.connection

    def _create_connection_factory(self):
        import org.apache.activemq.command.ActiveMQTextMessage as TextMessage
        import org.apache.activemq.command.ActiveMQBytesMessage as BytesMessage
        self.TextMessage = TextMessage
        self.BytesMessage = BytesMessage
        try:
            self._get_activemq_connection_factory_with_hashtable()
        except:
            self._get_activemq_connection_factory()

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
        self.connectionFactory = self.jndiContext.lookup(self.connection_factory_name)