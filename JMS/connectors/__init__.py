from .weblogic_connector import WeblogicConnector
from .activemq_connector import ActivemqConnector

available_connectors = {"activemq": ActivemqConnector,
             "weblogic": WeblogicConnector}