"""WFX authorization service package (abstract base + default no-op allow-all implementation)."""

from wfx.services.authorization.base import (
    PUBLIC_ANONYMOUS_ACTOR_ID,
    AdministrationResource,
    AuthorizationAuditEvent,
    AuthorizationMutation,
    AuthorizationMutationKind,
    AuthorizationMutationRejected,
    AuthorizationPrincipal,
    BaseAuthorizationService,
    DirectoryMembershipClaimState,
    DirectoryMembershipIngestResult,
    DirectoryMembershipSnapshot,
    ExecutionPrincipal,
    PublicAuthorizationRequest,
    PublicResourceAction,
    ResourceVisibilityScope,
    ShareRuleSnapshot,
    UserAuthorizationSnapshot,
)
from wfx.services.authorization.service import AuthorizationService

__all__ = [
    "PUBLIC_ANONYMOUS_ACTOR_ID",
    "AdministrationResource",
    "AuthorizationAuditEvent",
    "AuthorizationMutation",
    "AuthorizationMutationKind",
    "AuthorizationMutationRejected",
    "AuthorizationPrincipal",
    "AuthorizationService",
    "BaseAuthorizationService",
    "DirectoryMembershipClaimState",
    "DirectoryMembershipIngestResult",
    "DirectoryMembershipSnapshot",
    "ExecutionPrincipal",
    "PublicAuthorizationRequest",
    "PublicResourceAction",
    "ResourceVisibilityScope",
    "ShareRuleSnapshot",
    "UserAuthorizationSnapshot",
]
