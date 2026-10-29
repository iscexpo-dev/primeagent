"""Factory for Primeagent's database-backed connection resolver."""

from typing_extensions import override

from primeagent.services.connection.service import DatabaseConnectionResolverService
from primeagent.services.factory import ServiceFactory
from primeagent.services.schema import ServiceType


class ConnectionResolverServiceFactory(ServiceFactory):
    name = ServiceType.CONNECTION_RESOLVER_SERVICE.value

    def __init__(self) -> None:
        super().__init__(DatabaseConnectionResolverService)

    @override
    def create(self) -> DatabaseConnectionResolverService:
        return self.service_class()
