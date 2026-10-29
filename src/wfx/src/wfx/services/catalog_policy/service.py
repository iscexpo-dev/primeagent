"""Default fail-open catalog-policy service for standalone WFX."""

from __future__ import annotations

from wfx.log.logger import logger
from wfx.services import register_service
from wfx.services.catalog_policy.base import BaseCatalogPolicyService, CatalogPolicySnapshot
from wfx.services.policy_bundle import BasePolicyBundleService, PolicyBundleService, PolicyBundleSnapshot
from wfx.services.schema import ServiceType


@register_service(ServiceType.CATALOG_POLICY_SERVICE)
class CatalogPolicyService(BaseCatalogPolicyService):
    """Standalone default with an immutable empty, allow-all snapshot."""

    def __init__(self, policy_bundle_service: BasePolicyBundleService | None = None) -> None:
        super().__init__()
        self._policy_bundle_service = policy_bundle_service or PolicyBundleService()
        self.set_ready()
        logger.debug("Catalog policy service initialized (allow all)")

    @property
    def name(self) -> str:
        """Return the canonical service-type name."""
        return ServiceType.CATALOG_POLICY_SERVICE.value

    @property
    def snapshot(self) -> CatalogPolicySnapshot:
        """Return the immutable allow-all snapshot."""
        bundle = self._policy_bundle_service.snapshot
        return CatalogPolicySnapshot(
            blocked_component_keys=bundle.blocked_component_keys,
            blocked_template_keys=bundle.blocked_template_keys,
        )

    @property
    def policy_bundle_snapshot(self) -> PolicyBundleSnapshot:
        return self._policy_bundle_service.snapshot

    @property
    def supports_policy_bundle_updates(self) -> bool:
        return True

    def apply_policy_bundle(self, snapshot: PolicyBundleSnapshot) -> bool:
        return self._policy_bundle_service.publish(snapshot)
