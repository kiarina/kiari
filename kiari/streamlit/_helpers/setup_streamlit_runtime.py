import asyncio
import atexit
import threading
from dataclasses import dataclass, field

from kiari.core.finalizer import run_finalizers
from kiari.core.runtime import setup_runtime

from .._schemas.streamlit_startup_options import StreamlitStartupOptions
from ..streamlit_handler import StreamlitHandler, streamlit_handler_registry


@dataclass
class StreamlitRuntime:
    startup_options: StreamlitStartupOptions
    handler: StreamlitHandler
    agent_locks: dict[str, threading.Lock] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def get_agent_lock(self, agent_id: str) -> threading.Lock:
        with self.lock:
            return self.agent_locks.setdefault(agent_id, threading.Lock())


async def setup_streamlit_runtime(
    startup_options: StreamlitStartupOptions,
) -> StreamlitRuntime:
    await setup_runtime(startup_options.profile_name, startup_options.run_options)
    handler = streamlit_handler_registry.resolve(
        startup_options.run_options.streamlit_handler,
        profile_name=startup_options.profile_name,
        run_options=startup_options.run_options,
    )
    runtime = StreamlitRuntime(startup_options=startup_options, handler=handler)

    def finalize() -> None:
        asyncio.run(run_finalizers(startup_options.run_options.finalizers))

    atexit.register(finalize)
    return runtime
