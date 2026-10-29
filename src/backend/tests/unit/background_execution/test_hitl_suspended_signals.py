"""HITL substrate enums: SUSPENDED job status + PAUSE/RESUME signals (LE-1438).

Slice 1 (unit): the enum members exist on both the primeagent models and the wfx
mirror, so the later suspend/resume features have values to write and consume.

Slice 2 (real_services, load-bearing): a real INSERT of a ``suspended`` job and
``pause``/``resume`` signals against a REAL migrated DB commits and reads back
equal on BOTH SQLite and Postgres. A Python enum-membership check passes even if
the Postgres ``ALTER TYPE ... ADD VALUE`` never ran, so only a real insert
against the native enum types proves the migration added the values.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from primeagent.services.database.models.jobs.model import JobStatus, SignalType


def test_should_expose_suspended_when_reading_job_status_enum() -> None:
    assert JobStatus.SUSPENDED.value == "suspended"


def test_should_expose_pause_and_resume_when_reading_signal_type_enum() -> None:
    assert SignalType.PAUSE.value == "pause"
    assert SignalType.RESUME.value == "resume"


def test_should_keep_prior_members_when_adding_hitl_values() -> None:
    assert SignalType.STOP.value == "stop"
    assert {s.value for s in JobStatus} >= {
        "queued",
        "in_progress",
        "completed",
        "failed",
        "cancelled",
        "timed_out",
        "suspended",
    }


def test_should_mirror_suspended_in_wfx_job_status_copy() -> None:
    from wfx.schema.workflow import JobStatus as WfxJobStatus

    assert WfxJobStatus.SUSPENDED.value == "suspended"


@pytest.mark.real_services
@pytest.mark.no_blockbuster
async def test_should_persist_suspended_status_when_inserted_into_migrated_db(
    real_services_job_service,
) -> None:
    service = real_services_job_service
    job_id = uuid4()
    await service.create_job(job_id=job_id, flow_id=uuid4(), user_id=uuid4())

    await service.update_job_status(job_id, JobStatus.SUSPENDED)

    fetched = await service.get_job_by_job_id(job_id)
    assert fetched.status == JobStatus.SUSPENDED


@pytest.mark.real_services
@pytest.mark.no_blockbuster
async def test_should_persist_pause_and_resume_signals_when_inserted_into_migrated_db(
    real_services_job_service,
) -> None:
    service = real_services_job_service
    job_id = uuid4()
    await service.create_job(job_id=job_id, flow_id=uuid4(), user_id=uuid4())

    await service.write_signal(job_id, SignalType.PAUSE, {"request_id": "r1"})
    await service.write_signal(job_id, SignalType.RESUME, {"request_id": "r1", "decision": "approve"})

    signals = await service.unconsumed_signals(job_id)
    by_type = {s.signal_type: s.data for s in signals}
    assert by_type[SignalType.PAUSE] == {"request_id": "r1"}
    assert by_type[SignalType.RESUME] == {"request_id": "r1", "decision": "approve"}
