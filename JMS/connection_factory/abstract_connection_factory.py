from abc import ABC, abstractmethod

class AbstractConnectionFactory(ABC):
# class AbstractConnectionFactory():

    def __init__(self, server: str, port: int, username: str, password: str, connection_factory_name: str) -> None:
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.connection_factory_name = connection_factory_name
        self.connection = None
        self.session = None
        self.TextMessage = None
        self.BytesMessage = None
        self._create_connection_factory()
        self._create_connection()

    @abstractmethod
    def _create_connection(self):
        pass

    @abstractmethod
    def _create_connection_factory(self):
        pass