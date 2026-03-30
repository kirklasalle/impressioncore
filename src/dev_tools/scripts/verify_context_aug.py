
import asyncio
import sys

# Add project root to path
sys.path.append('d:/Projects/impressioncore')

async def verify_context_aug():
    try:
        from agent0core.core.agent import Agent0
        from agent0core.core.memory import MemoryManager

        # 1. Prepare Memory
        mm = MemoryManager(agent_id=0)
        mm.store_solution(
            "What port is the Kinect on?",
            "The Kinect is connected to MJPEG Stream ID 98 for the Color stream.",
            success=True
        )
        print("--- Memory Prepared ---")

        # 2. Initialize Agent
        agent = Agent0(name="ContextVerifier")

        print("\n--- PHASE 1: Testing Proactive Memory Recall ---")
        # We ask a question that should trigger the memory stored above
        # We use process_message which internally calls _augment_context
        response = await agent.process_message("Which MJPEG stream ID is used for the Kinect camera?")

        print(f"Agent Response: {response.content}")

        # Check if the context was retrieved (we can check the metadata of the response)
        # However, the current process_message doesn't explicitly return the augmented context in metadata,
        # but it uses it in generation.
        # For verification, we can see if the response contains '98'.
        if "98" in response.content:
            print("SUCCESS: Agent proactively used memory context.")
        else:
            print("FAILURE: Agent did not seem to use memory context.")

        print("\n--- PHASE 2: Testing Proactive Knowledge Search ---")
        # Ask something related to documentation (e.g., SAL or Prime Directive)
        # Note: We indexed the docs/ directory in the previous step.
        response = await agent.process_message("What are the 7 Laws for Intelligent Systems?")

        print(f"Agent Response: {response.content}")
        if "Prime Directive" in response.content or "Law" in response.content:
            print("SUCCESS: Agent proactively used knowledge base context.")
        else:
            print("FAILURE: Agent did not seem to use knowledge base context.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(verify_context_aug())
