from primeagent.utils import connection_string_parser as primeagent_parser
from wfx.utils import connection_string_parser as wfx_parser


def test_primeagent_reexports_wfx_helper():
    """The primeagent module is a shim; behavior is tested in src/wfx/tests/unit/utils."""
    assert primeagent_parser.transform_connection_string is wfx_parser.transform_connection_string
    assert primeagent_parser.transform_connection_string("protocol:user:p/ss@host") == "protocol:user:p%2Fss@host"
