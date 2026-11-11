
from qlogicae_cor.v3.library.cli_app_manager import (
    CliAppManager    
)


CliAppManager().get_singleton().run(
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
