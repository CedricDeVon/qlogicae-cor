
from qlogicae_cor.v3.library.external_dependency_manager import (
    ExternalDependencyManager
)
from qlogicae_cor.v3.library.plugin_manager import (
    PluginManager
)

PluginManager().get_singleton().setup(
    target_filesystem_paths=(
        "./sandbox/qlogicae_cor/v3/cli/plugin",
    ),
    is_recursive=True,
    imported_modules=(),
    raw_export_data=(),
    # "initial_export_data": {},
)

# for key, value in PluginManager().get_singleton().module_exports.items():
#     print(
#         f"{key}: {value}"
#     )
