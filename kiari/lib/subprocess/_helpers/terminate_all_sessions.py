from .get_subprocess_manager import get_subprocess_manager


def terminate_all_sessions() -> None:
    subprocess_manager = get_subprocess_manager()
    subprocess_manager.terminate_all_sessions()
