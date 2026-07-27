import os
import tempfile
from pathlib import Path

import uvicorn

from kiari.core.profile import ProfileName, RunOptions
from kiari.fastapi import FastAPIStartupOptions
from kiari.fastapi._constants import FASTAPI_STARTUP_FILE_ENV_VAR


def run_fastapi(profile_name: ProfileName, run_options: RunOptions) -> None:
    startup_options = FastAPIStartupOptions(
        profile_name=profile_name,
        run_options=run_options,
    )
    previous_startup_file = os.environ.get(FASTAPI_STARTUP_FILE_ENV_VAR)

    with tempfile.TemporaryDirectory(prefix="kiari-fastapi-") as temporary_dir:
        startup_file = Path(temporary_dir) / "startup.json"
        file_descriptor = os.open(
            startup_file,
            os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            0o600,
        )

        with os.fdopen(file_descriptor, "w") as file:
            file.write(startup_options.model_dump_json())

        os.environ[FASTAPI_STARTUP_FILE_ENV_VAR] = str(startup_file)

        try:
            uvicorn.run(
                "kiari.fastapi.app:create_app",
                factory=True,
                host=run_options.fastapi_host,
                port=run_options.fastapi_port,
                workers=run_options.fastapi_workers,
                reload=run_options.fastapi_workers is None,
            )
        finally:
            if previous_startup_file is None:
                os.environ.pop(FASTAPI_STARTUP_FILE_ENV_VAR, None)
            else:
                os.environ[FASTAPI_STARTUP_FILE_ENV_VAR] = previous_startup_file
