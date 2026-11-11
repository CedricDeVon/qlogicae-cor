
from qlogicae_cor.v3.library.external_dependency_manager import (
    ExternalDependencyManager
)
from qlogicae_cor.v3.library.cli_app_manager import (
    CliAppManager    
)

# ExternalDependencyManager().get_singleton().setup(
#     is_pre_allocated=True
# )

# ExternalDependencyManager().get_singleton().is_pre_allocated = True

CliAppManager().get_singleton().run(
    external_dependency={
        "is_pre_allocated": False,
    },
    plugin={
        "target_filesystem_paths": (
            "./sandbox/qlogicae_cor/v3/cli/plugin",
        ),
        "is_recursive": True,
        "imported_modules": (),
        "raw_export_data": (),
        # "initial_export_data": {},
    },
)
