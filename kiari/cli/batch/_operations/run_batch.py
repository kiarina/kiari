from kiarina.agi.agent import run_agent

from kiari.core.profile import ProfileName, RunOptions

from ..batch_handler import BatchRequest, batch_handler_registry


async def run_batch(
    profile_name: ProfileName,
    run_options: RunOptions,
    request: BatchRequest,
) -> None:
    batch_handler = batch_handler_registry.resolve(
        run_options.batch_handler,
        profile_name=profile_name,
        run_options=run_options,
    )

    async with batch_handler.handle_request(request) as session:
        async for event in run_agent(**session.as_run_agent_kwargs()):
            await batch_handler.on_agent_event(session, event)
            session.last_event = event

    if run_options.output_text:
        if session.last_event is None:  # pragma: no cover
            raise AssertionError("No events were generated during the agent run")

        print(session.last_event.to_text().strip(), end="")
