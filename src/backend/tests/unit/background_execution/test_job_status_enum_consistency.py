"""Drift guard for the JobStatus enum, which is defined in three places.

``JobStatus`` is intentionally mirrored across:
  - ``wfx.schema.workflow`` — the public workflow schema,
  - ``wfx.services.durable.models`` — the durable substrate's row models,
  - ``primeagent.services.database.models.jobs.model`` — the SQLAlchemy-bound
    model whose values persist to the ``job_status_enum`` column.

They compare by value (all are ``str`` enums), but membership / set-building /
``isinstance`` checks diverge the moment one copy gains or loses a member. A run
suspended by one runtime must read the same vocabulary when resumed through
another, so the three MUST stay identical. If a future change adds a status to
one and not the others (as almost happened when ``SUSPENDED`` landed), this test
fails in CI instead of silently mistreating a resumable job as terminal.

If/when the three are consolidated into a single canonical enum, delete this test.
"""

from __future__ import annotations

from primeagent.services.database.models.jobs.model import JobStatus as DbJobStatus
from wfx.schema.workflow import JobStatus as SchemaJobStatus
from wfx.services.durable.models import JobStatus as DurableJobStatus


def _members(enum_cls) -> set[tuple[str, str]]:
    return {(member.name, member.value) for member in enum_cls}


def test_all_job_status_definitions_have_identical_members():
    schema = _members(SchemaJobStatus)
    durable = _members(DurableJobStatus)
    db = _members(DbJobStatus)

    assert schema == durable, (
        f"JobStatus drift between wfx.schema.workflow and wfx.services.durable.models: {schema ^ durable}"
    )
    assert schema == db, (
        "JobStatus drift between wfx.schema.workflow and the DB model "
        "(primeagent.services.database.models.jobs.model): "
        f"{schema ^ db}"
    )


def test_suspended_is_present_in_every_definition():
    """The HITL state that motivated this guard must exist everywhere."""
    for enum_cls in (SchemaJobStatus, DurableJobStatus, DbJobStatus):
        assert "suspended" in {m.value for m in enum_cls}
