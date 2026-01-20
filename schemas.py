
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Literal


class AgentDecision(BaseModel):
    """
    Decision schema returned by the LLM on every step.
    This schema is used to decide which tool to call next.
    """

    thought: str = Field(
        ...,
        description=(
            "Internal reasoning used by the agent to decide the next action. "
            "This is NOT shown to the end user."
        ),
    )

    action: Literal[
        "get_transaction_details",
        "error_handler",
        "output"
    ] = Field(
        ...,
        description=(
            "The next action the agent must take. "
            "Must be one of the allowed tool names."
        ),
    )

    action_input: Dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "JSON object containing the input arguments for the selected action. "
            "If action is 'output', this contains the final response message."
        ),
    )








