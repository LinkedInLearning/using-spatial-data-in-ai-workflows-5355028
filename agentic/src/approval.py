"""
Human-in-the-Loop Approval

This module provides functions for human approval of agent actions.
Human-in-the-loop is important for AI agents to ensure transparency and control.
"""


def human_approval(action_description: str, query_details: str) -> bool:
    """
    Pause execution and ask human for approval before proceeding.

    This function implements "human-in-the-loop" - a safety pattern where
    AI agents must get human approval before taking certain actions.

    Why Human-in-the-Loop?
    - Transparency: You see what the agent wants to do
    - Control: You can stop unwanted actions
    - Learning: You understand the agent's decision-making process
    - Safety: Prevents unintended data access or actions

    Args:
        action_description: What the agent wants to do
        query_details: Specific details about the action

    Returns:
        True if approved, False if rejected

    Example:
        approved = human_approval(
            "Query Overture Maps for 'coffee_shop' places in Seattle",
            "Area: Seattle, WA\\nCategory: coffee_shop\\nBounding box: ..."
        )
        if approved:
            # proceed with query
            pass
    """
    print("\n" + "=" * 60)
    print("🤖 AGENT REQUESTING APPROVAL")
    print("=" * 60)
    print(f"\nAction: {action_description}")
    print(f"\nDetails:\n{query_details}")
    print("\n" + "=" * 60)

    # Get human input
    response = input("\n✅ Approve this action? (yes/no): ").strip().lower()

    approved = response in ['yes', 'y']

    if approved:
        print("\n✅ APPROVED - Proceeding...\n")
    else:
        print("\n❌ REJECTED - Action cancelled.\n")

    return approved
