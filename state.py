from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

class AgentState(BaseModel):

    messages: List[BaseMessage] = Field(default_factory=list)

    tool_result: Optional[dict] = None

    txn_id: Optional[str] = None
    txn_status: Optional[str] = None
    has_identified_transaction: bool = False
