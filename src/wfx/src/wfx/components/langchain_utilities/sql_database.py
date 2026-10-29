from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from wfx.custom.custom_component.component import Component
from wfx.io import (
    Output,
    StrInput,
)
from wfx.utils.ssrf_protection import validate_connector_database_url_for_ssrf


class SQLDatabaseComponent(Component):
    display_name = "SQLDatabase"
    description = "SQL Database"
    name = "SQLDatabase"
    icon = "LangChain"

    inputs = [
        StrInput(name="uri", display_name="URI", info="URI to the database.", required=True),
    ]

    outputs = [
        Output(display_name="SQLDatabase", name="SQLDatabase", method="build_sqldatabase"),
    ]

    def clean_up_uri(self, uri: str) -> str:
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://")
        return uri.strip()

    def build_sqldatabase(self) -> SQLDatabase:
        uri = self.clean_up_uri(self.uri)
        # Security: block SSRF to internal databases and local-file dialects (the tenant
        # controls this URI).
        validate_connector_database_url_for_ssrf(uri)
        # Create an engine using SQLAlchemy with StaticPool
        engine = create_engine(uri, poolclass=StaticPool)
        return SQLDatabase(engine)
