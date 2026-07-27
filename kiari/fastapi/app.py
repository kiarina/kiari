from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from types import TracebackType

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from kiarina.agi.agent import run_agent
from kiarina.utils.app import AppAlreadyConfiguredError, configure

from kiari.core.finalizer import run_finalizers
from kiari.core.runtime import setup_runtime

from ._helpers.load_fastapi_startup_options import load_fastapi_startup_options
from ._schemas.fastapi_startup_options import FastAPIStartupOptions
from ._schemas.request_body import RequestBody
from .fastapi_handler import FastAPIHandler, FastAPIRequest, fastapi_handler_registry


def create_app(startup_options: FastAPIStartupOptions | None = None) -> FastAPI:
    startup_options = startup_options or load_fastapi_startup_options()
    with suppress(AppAlreadyConfiguredError):
        configure(app_author="kiarina", app_name="kiari")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        await setup_runtime(
            startup_options.profile_name,
            startup_options.run_options,
        )
        app.state.fastapi_handler = fastapi_handler_registry.resolve(
            startup_options.run_options.fastapi_handler,
            profile_name=startup_options.profile_name,
            run_options=startup_options.run_options,
        )

        try:
            yield
        finally:
            await run_finalizers(startup_options.run_options.finalizers)

    app = FastAPI(lifespan=lifespan)

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(startup_options.run_options.fastapi_path)
    async def run(request_body: RequestBody, request: Request) -> StreamingResponse:
        handler: FastAPIHandler = request.app.state.fastapi_handler
        fastapi_request = FastAPIRequest(
            body=request_body,
            headers=dict(request.headers),
        )
        request_context = handler.handle_request(fastapi_request)
        session = await request_context.__aenter__()

        async def event_generator() -> AsyncIterator[str]:
            exit_args: tuple[
                type[BaseException] | None,
                BaseException | None,
                TracebackType | None,
            ] = (
                None,
                None,
                None,
            )

            try:
                try:
                    async for event in run_agent(**session.as_run_agent_kwargs()):
                        result_event = await handler.on_agent_event(session, event)

                        if result_event is not None:
                            yield result_event.model_dump_json() + "\n"

                        session.last_event = event

                    if session.last_event is None:
                        raise RuntimeError("Agent completed without generating any events")

                    result_event = await handler.on_agent_completed(
                        session,
                        session.last_event,
                    )

                    if result_event is not None:
                        yield result_event.model_dump_json() + "\n"

                except Exception as e:
                    result_event = await handler.on_agent_error(session, e)

                    if result_event is not None:
                        yield result_event.model_dump_json() + "\n"

            except BaseException as e:
                exit_args = (type(e), e, e.__traceback__)
                raise

            finally:
                await request_context.__aexit__(*exit_args)

        return StreamingResponse(
            event_generator(),
            media_type="application/x-ndjson",
        )

    return app
