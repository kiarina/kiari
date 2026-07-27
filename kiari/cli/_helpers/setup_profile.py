from kiari.core.profile import ProfileName, RunOptions, RunSpec, profile_store

from .._types.save_mode import SaveMode


def setup_profile(
    profile_name: ProfileName | None,
    save_mode: SaveMode | None,
    run_spec: RunSpec,
) -> tuple[ProfileName, RunSpec, RunOptions]:
    if not profile_name:
        profile_name = profile_store.get_current()

    if save_mode != "reset":
        run_spec = {
            **profile_store.load_run_spec(profile_name),
            **run_spec,
        }

    if save_mode in ("set", "reset"):
        profile_store.save_run_spec(profile_name, run_spec)

    run_options = RunOptions.model_validate(run_spec)
    return profile_name, run_spec, run_options
