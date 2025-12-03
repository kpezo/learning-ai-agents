"""Interactive quiz runner with adaptive difficulty.

This runner uses the educational agent system with:
- Tutor, Curriculum Planner, and Assessor agents
- Adaptive difficulty adjustment (6 levels)
- Question type filtering by difficulty
- Automatic scaffolding support when struggling

Run with: python -m adk.run_quiz
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

from adk.agent import root_agent


async def run_quiz_session():
    """Run an interactive quiz session with adaptive difficulty."""
    session_service = InMemorySessionService()
    memory_service = InMemoryMemoryService()

    runner = Runner(agent=root_agent, app_name="education_app", **{
        "session_service": session_service,
        "memory_service": memory_service,
        "plugins": [LoggingPlugin()],
    })

    session_id = f"quiz-{uuid.uuid4().hex[:8]}"
    user_id = "demo_user"

    # Create session
    await session_service.create_session(
        app_name="education_app",
        user_id=user_id,
        session_id=session_id,
    )

    print("\n" + "="*70)
    print("  ADAPTIVE QUIZ SYSTEM")
    print("="*70)
    print(f"\nSession ID: {session_id}")
    print(f"User ID: {user_id}")
    print("\nCommands:")
    print("  - Type your answer to questions")
    print("  - Type '/exit' to quit")
    print("  - Type '/stats' to see learning statistics")
    print("="*70 + "\n")

    def _pretty(text: str) -> str:
        """Format JSON-like text for better readability."""
        try:
            obj = json.loads(text)
            return json.dumps(obj, indent=2, ensure_ascii=False)
        except Exception:
            return text.replace("\\n", "\n")

    async def send(message_text: str):
        """Send a message and display response."""
        user_content = types.Content(role="user", parts=[types.Part(text=message_text)])

        print(f"\n{'─'*70}")
        print("Processing...")
        print(f"{'─'*70}\n")

        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=user_content
        ):
            if event.content and event.content.parts:
                parts = event.content.parts
                is_final = event.is_final_response()
                prefix = "📤 RESPONSE" if is_final else "⚙️  STEP"

                for part in parts:
                    if hasattr(part, "function_call") and part.function_call:
                        if not is_final:  # Only show intermediate tool calls
                            print(f"{prefix}: Calling {part.function_call.name}")
                    elif hasattr(part, "function_response") and part.function_response:
                        if not is_final:  # Only show intermediate responses
                            print(f"{prefix}: Tool response received")
                    elif hasattr(part, "text") and part.text and part.text != "None":
                        if is_final:  # Only show final text responses
                            display = _pretty(part.text)
                            print(f"\n{display}\n")

    # Initial greeting - instruct agent to extract topics from PDF first
    greeting = (
        "I want to take a quiz on content from the PDF. "
        "First, use the extract_topics_from_pdf tool to analyze the PDF and show me available topics. "
        "Present the topics in a clear, numbered list so I can choose one. "
        "Once I select a topic, prepare a quiz using the adaptive difficulty system."
    )

    await send(greeting)

    # Interactive loop
    while True:
        user_input = input("\nYou: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "/exit":
            print("\n" + "="*70)
            print("  Quiz session ended. Thank you for learning!")
            print("="*70 + "\n")
            break

        if user_input.lower() == "/stats":
            await send("Show me my learning statistics and weak concepts.")
            continue

        await send(user_input)


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env", override=True)

    print("\n🎓 Starting Adaptive Quiz System...")

    try:
        asyncio.run(run_quiz_session())
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("  Quiz interrupted. Goodbye!")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
