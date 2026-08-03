from JMS.connection_factory.abstract_connection_factory import AbstractConnectionFactory

class WeblogicConnectionFactory(AbstractConnectionFactory):

    def create_queue(self, name: str):
        return self.jndiContext.lookup(name)

    def create_topic(self, name: str):
        return self.session.createTopic(name)

    def _create_connection(self):
        try:
            from javax.jms import Session
        except ImportError:
            from jakarta.jms import Session
        self.connection = self.connectionFactory.createConnection()
        self.session = self.connection.createSession(
            False, Session.AUTO_ACKNOWLEDGE
        )
        return self.connection

    def _create_connection_factory(self):
        import weblogic.jms.common.TextMessageImpl as TextMessage
        import weblogic.jms.common.BytesMessageImpl as BytesMessage
        self.TextMessage = TextMessage
        self.BytesMessage = BytesMessage
        self._get_weblogic_connection_factory_with_environment()

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
        self.connectionFactory = self.jndiContext.lookup(self.connection_factory_name)

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
        self.connectionFactory = self.jndiContext.lookup(self.connection_factory_name)
