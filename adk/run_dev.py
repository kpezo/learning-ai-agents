"""Local dev runner for the ADK education agents.

Streams events so you can see tool calls and intermediate steps. Aligns with
Day3/Day4 guidance (sessions, memory, compaction, observability).
"""

import asyncio
import json
import uuid
from pathlib import Path

from dotenv import load_dotenv

from google.adk.memory import InMemoryMemoryService
from google.adk.plugins.logging_plugin import LoggingPlugin
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from adk.question_pipeline import root_agent


async def run_once(message: str):
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    runner = Runner(agent=root_agent, app_name="agents", **{
        "session_service": session_service,
        "memory_service": memory_service,
        "plugins": [LoggingPlugin()],
    })

    session_id = f"session-{uuid.uuid4().hex[:8]}"
    user_id = "demo_user"

    # Ensure session exists before running.
    await session_service.create_session(
        app_name="agents",
        user_id=user_id,
        session_id=session_id,
    )

    print("Commands: type your answer, /exit to quit.")
    print(f"\n== Session {session_id} ==\n")

    def _pretty(text: str) -> str:
        """Format JSON-like text and normalize escaped newlines for nicer CLI output."""
        try:
            obj = json.loads(text)
            return json.dumps(obj, indent=2, ensure_ascii=False)
        except Exception:
            return text.replace("\\n", "\n")

    async def send(message_text: str):
        user_content = types.Content(role="user", parts=[types.Part(text=message_text)])
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=user_content
        ):
            if event.content and event.content.parts:
                parts = event.content.parts
                prefix = "(final)" if event.is_final_response() else "(step)"
                for part in parts:
                    if hasattr(part, "function_call") and part.function_call:
                        print(f"{prefix} function_call: {part.function_call}\n")
                    elif hasattr(part, "function_response") and part.function_response:
                        print(f"{prefix} function_response: {part.function_response}\n")
                    elif hasattr(part, "text") and part.text and part.text != "None":
                        display = _pretty(part.text)
                        print(f"{prefix} {display}\n")

    # Kick off with the scenario prompt.
    await send(message)

    # Interactive loop
    while True:
        user_in = input("You (/exit): ").strip()
        if not user_in:
            continue
        if user_in.lower() == "/exit":
            print("Exiting session.")
            break
        await send(user_in)


def main():
    # Load .env from repo root explicitly to ensure keys are present.
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)
    scenario = (
        "Ingest the PDF (PDF_PATH env or Intro.pdf), extract main concepts and their relationships,"
        " classify declarative/procedural/conditional knowledge, and propose clarifying questions."
        " Return the concepts, relationships, and 3–6 atomic questions to ask me next."
    )
    asyncio.run(run_once(scenario))


if __name__ == "__main__":
    main()
