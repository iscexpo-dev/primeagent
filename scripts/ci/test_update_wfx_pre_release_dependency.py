from scripts.ci.update_wfx_pre_release_dependency import update_wfx_requirements


def test_preserves_wfx_extras_and_markers():
    content = """
dependencies = ["wfx~=1.11.0"]
cassandra = ["wfx[cassandra]~=1.11.0"]
toolguard = ["wfx[toolguard]>=1.11.0; sys_platform != 'win32'"]
provider = ["wfx-openai>=0.1.0,<1.0.0"]
"""

    result = update_wfx_requirements(content, "1.11.0rc2")

    assert '"wfx==1.11.0rc2"' in result
    assert '"wfx[cassandra]==1.11.0rc2"' in result
    assert "\"wfx[toolguard]==1.11.0rc2; sys_platform != 'win32'\"" in result
    assert '"wfx-openai>=0.1.0,<1.0.0"' in result


def test_rewrites_an_existing_release_range_idempotently():
    content = 'dependencies = ["wfx[toolguard]>=1.11.0rc1,<1.12.dev0"]\n'

    result = update_wfx_requirements(content, "1.11.0rc2")

    assert result == 'dependencies = ["wfx[toolguard]==1.11.0rc2"]\n'
    assert update_wfx_requirements(result, "1.11.0rc2") == result
