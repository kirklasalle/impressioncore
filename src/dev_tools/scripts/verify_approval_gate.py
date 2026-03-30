
import asyncio
import sys

# Add project root to path
sys.path.append('d:/Projects/impressioncore')

async def verify_approval_gate():
    try:
        from agent0core.core.agent import Agent0

        # Initialize Agent
        agent = Agent0(name="GateVerifier")

        print("--- PHASE 1: Triggering High-Impact Action ---")
        # Trigger 'reset' on 'training' tool (correct tool name is 'training')
        result = await agent.execute_tool(
            tool_name="training",
            action="reset",
            params={}
        )

        print(f"Initial Result: {result.get('status') or result.get('error')}")

        if result.get('status') == 'approval_required':
            approval_id = result.get('approval_id')
            print(f"Gate Triggered! Approval ID: {approval_id}")

            print("\n--- PHASE 2: Approving the action ---")
            decision_result = await agent.decide_approval(approval_id, approved=True)
            print(f"Decision Result Status: {decision_result.get('status')}")

            if decision_result.get('status') == 'approved':
                print("SUCCESS: High-Impact Gate allowed re-execution after approval.")
                # The 'training' tool will return an 'error' because 'reset' is unknown to it,
                # but Agent0.decide_approval will still return status 'approved' with the error in 'result'
                print(f"Tool Execution Result: {decision_result.get('result', {}).get('error', 'Success')}")
            else:
                print(f"FAILURE: Unexpected status after approval: {decision_result.get('status')}")
        else:
            print(f"FAILURE: Gate was NOT triggered for 'reset' action. Result: {result}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(verify_approval_gate())
