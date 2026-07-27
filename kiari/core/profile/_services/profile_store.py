import logging
import shutil
from pathlib import Path

import yaml
from kiarina.utils.file import read_yaml_dict, write_yaml_dict
from pydantic import BaseModel, Field
from pydantic_settings_manager import UserConfigs

from kiari.core.paths import (
    get_profile_config_file_path,
    get_profile_run_spec_file_path,
    get_profiles_dir_path,
    get_profiles_file_path,
)

from .._schemas.profile import Profile
from .._types.profile_name import ProfileName
from .._types.run_spec import RunSpec

logger = logging.getLogger(__name__)


class ProfileStore:
    class _Data(BaseModel):
        current: ProfileName = "default"
        profiles: dict[ProfileName, Profile] = Field(
            default_factory=lambda: {"default": Profile(name="default")}
        )

    def __init__(self) -> None:
        self._data: ProfileStore._Data | None = None

    @property
    def file_path(self) -> Path:
        return get_profiles_file_path()

    # --------------------------------------------------
    # Public Methods (Current Profile Name)
    # --------------------------------------------------

    def get_current(self) -> ProfileName:
        data = self._load_data()
        return data.current

    def set_current(self, profile_name: ProfileName) -> None:
        data = self._load_data()
        data.current = profile_name
        self._save_data(data)
        logger.debug(f"Set current profile to: {profile_name}")

    # --------------------------------------------------
    # Public Methods (Profiles)
    # --------------------------------------------------

    def list_profiles(self) -> list[Profile]:
        data = self._load_data()
        return list(data.profiles.values())

    def has_profile(self, profile_name: ProfileName) -> bool:
        data = self._load_data()
        return profile_name in data.profiles

    def get_profile(self, profile_name: ProfileName | None = None) -> Profile:
        data = self._load_data()

        if profile_name is None:
            profile_name = data.current

        if profile := data.profiles.get(profile_name):
            return profile

        return Profile(name=profile_name)

    def set_profile(self, profile: Profile) -> None:
        data = self._load_data()
        data.profiles[profile.name] = profile
        self._save_data(data)
        logger.debug(f"Set profile: {profile.name}")

    def delete_profile(self, profile_name: ProfileName) -> None:
        data = self._load_data()

        if profile_name in data.profiles:
            del data.profiles[profile_name]
            self._save_data(data)
            logger.debug(f"Deleted profile: {profile_name}")

    # --------------------------------------------------
    # Public Methods (Run Spec)
    # --------------------------------------------------

    def load_run_spec(self, profile_name: ProfileName) -> RunSpec:
        data = read_yaml_dict(str(get_profile_run_spec_file_path(profile_name)))
        return self._validate_run_spec(data)

    def save_run_spec(self, profile_name: ProfileName, run_spec: RunSpec) -> None:
        write_yaml_dict(str(get_profile_run_spec_file_path(profile_name)), run_spec)
        logger.debug(f"Saved run spec for profile: {profile_name}")

    def delete_run_spec(self, profile_name: ProfileName) -> None:
        file_path = get_profile_run_spec_file_path(profile_name)

        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Deleted run spec for profile: {profile_name}")

    def ensure_run_spec(self, profile_name: ProfileName) -> bool:
        file_path = get_profile_run_spec_file_path(profile_name)

        if file_path.exists():
            return False

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(_get_run_spec_template(profile_name))
        logger.debug(f"Created run spec for profile: {profile_name}")
        return True

    # --------------------------------------------------
    # Public Methods (Config)
    # --------------------------------------------------

    def load_config(self, profile_name: ProfileName) -> UserConfigs:
        data = read_yaml_dict(str(get_profile_config_file_path(profile_name)))
        return self._validate_config(data)

    def save_config(self, profile_name: ProfileName, config: UserConfigs) -> None:
        write_yaml_dict(str(get_profile_config_file_path(profile_name)), config)
        logger.debug(f"Saved config for profile: {profile_name}")

    def delete_config(self, profile_name: ProfileName) -> None:
        file_path = get_profile_config_file_path(profile_name)

        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Deleted config for profile: {profile_name}")

    def ensure_config(self, profile_name: ProfileName) -> bool:
        file_path = get_profile_config_file_path(profile_name)

        if file_path.exists():
            return False

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(_get_config_template(profile_name))
        logger.debug(f"Created config for profile: {profile_name}")
        return True

    # --------------------------------------------------
    # Public Methods (Test)
    # --------------------------------------------------

    def delete_all(self) -> None:  # pragma: no cover
        profiles_dir_path = get_profiles_dir_path()

        if profiles_dir_path.exists():
            shutil.rmtree(profiles_dir_path)

        profiles_file_path = get_profiles_file_path()

        if profiles_file_path.exists():
            profiles_file_path.unlink()

        self._data = None

    # --------------------------------------------------
    # Private Methods
    # --------------------------------------------------

    def _load_data(self) -> _Data:
        if self._data is not None:
            return self._data

        try:
            data_dict = read_yaml_dict(str(self.file_path))

        except yaml.YAMLError as e:  # pragma: no cover
            logger.warning(f"Failed to read profiles data from {self.file_path}, error: {e}")
            self._data = self._Data()
            return self._data

        if not data_dict:
            self._data = self._Data()
            return self._data

        try:
            self._data = self._Data.model_validate(data_dict)

            logger.debug(f"Loaded {len(self._data.profiles)} profiles from {self.file_path}")

            return self._data

        except Exception as e:  # pragma: no cover
            logger.warning(f"Failed to parse profiles data: {e}")
            self._data = self._Data()
            return self._data

    def _save_data(self, data: _Data) -> None:
        self._data = data
        write_yaml_dict(str(self.file_path), data.model_dump(mode="json"))
        logger.debug(f"Saved {len(data.profiles)} profiles to {self.file_path}")

    def _validate_run_spec(self, data: object) -> RunSpec:
        if data is None:
            return {}

        if not isinstance(data, dict):
            logger.warning(f"Expected mapping data, got {type(data)}")
            return {}

        return {k: v for k, v in data.items() if isinstance(k, str)}

    def _validate_config(self, data: object) -> UserConfigs:
        if data is None:
            return {}

        if not isinstance(data, dict):
            logger.warning(f"Expected mapping data, got {type(data)}")
            return {}

        return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, dict)}


def _get_run_spec_template(profile_name: str) -> str:
    return f"""# RunSpec for profile: {profile_name}
# You can customize this file to set up your default RunSpec for this profile.
# For more information on the RunSpec format, see:
# https://kiarina.github.io/kiari/
# Example RunSpec content:
# chat_model: gpt-5.4
"""


def _get_config_template(profile_name: str) -> str:
    return f"""# Config for profile: {profile_name}
# You can customize this file to set up your default config for this profile.
# For more information on the config format, see:
# https://kiarina.github.io/kiari/
# Example config content:
# chat_model: gpt-5.4
"""


profile_store = ProfileStore()
