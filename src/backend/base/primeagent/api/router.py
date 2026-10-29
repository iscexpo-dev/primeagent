# Router for base api
from fastapi import APIRouter, Depends
from wfx.schema.workflow import WORKFLOW_EXECUTION_RESPONSES
from wfx.services.settings.feature_flags import FEATURE_FLAGS
from wfx.workflow.host import WorkflowHost
from wfx.workflow.router import create_workflow_router

from primeagent.api.v1 import (
    a2a_router,
    api_key_router,
    audits_router,
    authz_audit_router,
    authz_capabilities_router,
    authz_me_router,
    authz_role_assignments_router,
    authz_roles_router,
    authz_shares_router,
    authz_teams_router,
    catalog_policy_router,
    chat_router,
    connections_router,
    endpoints_router,
    extensions_router,
    files_router,
    flow_conflict_router,
    flow_events_router,
    flow_version_router,
    flows_audits_router,
    flows_router,
    folders_router,
    integrations_router,
    knowledge_bases_router,
    login_router,
    mcp_projects_router,
    mcp_router,
    memories_router,
    migration_router,
    model_options_router,
    model_provider_policy_router,
    models_router,
    monitor_router,
    openai_responses_router,
    policy_bundle_router,
    projects_audits_router,
    projects_router,
    starter_projects_router,
    store_router,
    traces_router,
    trigger_ingress_router,
    triggers_router,
    users_router,
    validate_router,
    variables_router,
)
from primeagent.api.v1.data_subjects import router as data_subjects_router
from primeagent.api.v1.data_subjects_self import router as data_subjects_self_router
from primeagent.api.v1.knowledge_base_storage import router as knowledge_base_storage_router
from primeagent.api.v1.voice_mode import router as voice_mode_router
from primeagent.api.v2 import files_router as files_router_v2
from primeagent.api.v2 import mcp_router as mcp_router_v2
from primeagent.api.v2 import registration_router as registration_router_v2
from primeagent.api.v2 import workflow_background_router as workflow_background_router_v2
from primeagent.api.v2 import workflow_public_router as workflow_public_router_v2
from primeagent.api.v2.workflow_host import PrimeagentWorkflowHost

router_v1 = APIRouter(
    prefix="/v1",
)
router_v1.include_router(knowledge_base_storage_router)

router_v2 = APIRouter(
    prefix="/v2",
)


def include_deployment_router(target_router: APIRouter) -> None:
    """Mount deployment routes only when the deployments feature is enabled."""
    if FEATURE_FLAGS.wxo_deployments:
        from primeagent.api.v1.deployments import router as deployment_router

        target_router.include_router(deployment_router)


def include_migration_router(target_router: APIRouter) -> None:
    """Mount the instance migration routes only when the feature is enabled."""
    if FEATURE_FLAGS.instance_migration:
        target_router.include_router(migration_router)


router_v1.include_router(flow_conflict_router)
router_v1.include_router(chat_router)
router_v1.include_router(connections_router)
router_v1.include_router(integrations_router)
router_v1.include_router(endpoints_router)
router_v1.include_router(validate_router)
router_v1.include_router(store_router)
router_v1.include_router(audits_router)
# Before flows_router, whose /{flow_id} would otherwise capture /audits and answer 422.
router_v1.include_router(flows_audits_router)
router_v1.include_router(flows_router)
router_v1.include_router(flow_events_router)
router_v1.include_router(flow_version_router)
router_v1.include_router(data_subjects_self_router)
router_v1.include_router(users_router)
router_v1.include_router(data_subjects_router)
router_v1.include_router(api_key_router)
router_v1.include_router(login_router)
router_v1.include_router(variables_router)
router_v1.include_router(files_router)
router_v1.include_router(monitor_router)
router_v1.include_router(traces_router)
router_v1.include_router(folders_router)
# Before projects_router, whose /{project_id} would otherwise capture /audits and answer 422.
router_v1.include_router(projects_audits_router)
router_v1.include_router(projects_router)
router_v1.include_router(starter_projects_router)
router_v1.include_router(knowledge_bases_router)
router_v1.include_router(memories_router)
router_v1.include_router(mcp_router)
router_v1.include_router(voice_mode_router)
router_v1.include_router(mcp_projects_router)
# Always mounted; the per-request guard in primeagent.api.v1.a2a returns 404 when
# PRIMEAGENT_A2A_ENABLED is off, so the route is indistinguishable from "not
# mounted" until the flag is set (mirrors the extensions router below).
router_v1.include_router(a2a_router)
router_v1.include_router(openai_responses_router)
router_v1.include_router(models_router)
router_v1.include_router(model_options_router)
router_v1.include_router(model_provider_policy_router)
router_v1.include_router(policy_bundle_router)
router_v1.include_router(authz_shares_router)
router_v1.include_router(authz_audit_router)
router_v1.include_router(authz_capabilities_router)
router_v1.include_router(authz_roles_router)
router_v1.include_router(authz_role_assignments_router)
router_v1.include_router(authz_teams_router)
router_v1.include_router(authz_me_router)
router_v1.include_router(catalog_policy_router)
router_v1.include_router(triggers_router)
# Unauthenticated by design: every route on it is provider-signed and answers
# 404 for anything it cannot verify. See api/v1/trigger_ingress.py.
router_v1.include_router(trigger_ingress_router)


# Mounted unconditionally: this module imports before load_dotenv(env_file), so the
# per-request guard in api.v1.extensions reads the live flag and 404s when it is off.
router_v1.include_router(extensions_router)
include_deployment_router(router_v1)
include_migration_router(router_v1)


# Agentic flow execution - lazy import to avoid circular dependency
def _include_agentic_router():
    from primeagent.agentic.api.deps import require_agentic_experience
    from primeagent.agentic.api.files_router import router as agentic_files_router
    from primeagent.agentic.api.router import router as agentic_router
    from primeagent.agentic.api.sessions_router import router as agentic_sessions_router
    from primeagent.api.v1.agentic_mcp import router as agentic_mcp_router

    # SECURITY (Issue 15): gate the sandbox-management routers on agentic_experience. The
    # code-exec endpoints inside agentic_router (/assist, /assist/stream, /execute) carry the same
    # gate per-route (see agentic/api/router.py) so the read-only /agentic/check-config probe stays
    # reachable for non-agentic deployments.
    agentic_gate = [Depends(require_agentic_experience)]
    router_v1.include_router(agentic_router)
    router_v1.include_router(agentic_files_router, dependencies=agentic_gate)
    router_v1.include_router(agentic_sessions_router, dependencies=agentic_gate)
    router_v1.include_router(agentic_mcp_router)


_include_agentic_router()

router_v2.include_router(files_router_v2)
router_v2.include_router(mcp_router_v2)
router_v2.include_router(registration_router_v2)

# POST /api/v2/workflows runs through the shared wfx router bound to the
# primeagent host. ``supports_background=True`` lets the background-submit branch
# dispatch to the host; ``auto_register_job_routes=False`` suppresses the wfx
# generic GET-status/POST-stop routes so the primeagent durable router below owns
# them (one handler per method+path). ``developer_api_guard=False`` because the
# authenticated primeagent v2 router has never carried a developer-api gate; the
# default-off setting would otherwise 403 every authenticated request.
# One host serves every profile. Warming is selected at request/build time from
# ``settings.warm_registry_enabled`` while authentication and per-flow authorization
# remain identical whether the cache is enabled or not. This module is imported before
# ``load_dotenv`` runs, so keeping the decision out of this path preserves ``--env-file``.
_workflow_host: WorkflowHost = PrimeagentWorkflowHost()
assert isinstance(_workflow_host, WorkflowHost)  # noqa: S101
router_v2.include_router(
    create_workflow_router(
        _workflow_host,
        developer_api_guard=False,
        auto_register_job_routes=False,
        responses=WORKFLOW_EXECUTION_RESPONSES,
    )
)
# The primeagent-owned durable routes: GET status, POST /stop, GET /{job_id}/events.
router_v2.include_router(workflow_background_router_v2)
router_v2.include_router(workflow_public_router_v2)

router = APIRouter(
    prefix="/api",
)
router.include_router(router_v1)
router.include_router(router_v2)
