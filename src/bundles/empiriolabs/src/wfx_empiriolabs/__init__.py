"""wfx-empiriolabs: EmpirioLabs bundle.

Distribution unit ``wfx-empiriolabs``.  At runtime Primeagent's loader discovers
``extension.json`` shipped alongside this ``__init__.py`` and registers the
bundle's components under the namespaced IDs
``ext:empiriolabs:EmpirioLabsModelComponent@official`` and
``ext:empiriolabs:EmpirioLabsImageGenerationComponent@official``.
"""

from wfx_empiriolabs.components.empiriolabs.empiriolabs import EmpirioLabsModelComponent
from wfx_empiriolabs.components.empiriolabs.empiriolabs_image_generation import EmpirioLabsImageGenerationComponent

__all__ = ["EmpirioLabsImageGenerationComponent", "EmpirioLabsModelComponent"]
