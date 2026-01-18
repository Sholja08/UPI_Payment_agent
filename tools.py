
"""
tools.py - Tool Assembly for Payment Agent
Combines MCP tools + Helper tools for the agent
"""

from langchain.tools import tool
from mcp_tools import get_mcp_tool_list


# ==========================================
# HELPER TOOLS
# ==========================================

@tool
def error_handler(error_message: str, error_code: str = "UNKNOWN", suggested_action: str = ""):
    """
    Standard error handling tool for agent failures.
    Use when:
    - MCP tool returns success: False
    - Invalid user input detected
    - Database errors occur
    - No results found
    
    Args:
        error_message: Description of what went wrong
        error_code: Error type (NO_RESULTS, DB_ERROR, INVALID_INPUT, UNKNOWN)
        suggested_action: What the user should try next
    
    Example:
        error_handler(
            error_message="No transactions found for date 2025-12-06",
            error_code="NO_RESULTS",
            suggested_action="Try a different date or remove filters"
        )
    
    Returns:
        Formatted error message for the user
    """
    response = f" Error: {error_message}"
    
    if suggested_action:
        response += f"\n Suggestion: {suggested_action}"
    
    return response


@tool
def output(final_response: str):
    """
    Final response tool for the agent.
    Use this tool when you're ready to return the final answer to the user.
    
    Args:
        final_response: The formatted answer to return
    
    Example:
        output("I found 3 transactions on 2025-12-06. Here are the details: ...")
    
    Always use this tool as the LAST step after:
    1. Getting data from get_transaction_details
    2. Formatting the results nicely
    3. Handling any errors with error_handler (if needed)
    
    Returns:
        The final response string
    """
    return final_response


# ==========================================
# ASSEMBLE ALL TOOLS
# ==========================================

def get_all_tools():
    """
    Combines MCP tools and helper tools for the agent.
    
    Returns:
        list: All tools available to the agent
    """
    # Get MCP tools from server
    mcp_tools = get_mcp_tool_list()
    
    # Add helper tools
    helper_tools = [error_handler, output]
    
    # Combine all tools
    all_tools = mcp_tools + helper_tools
    
    print(f" Assembled {len(all_tools)} tools for agent:")
    print(f"   - {len(mcp_tools)} MCP tool(s)")
    print(f"   - {len(helper_tools)} helper tool(s)")
    print()
    
    return all_tools


# ==========================================
# VERIFICATION TEST
# ==========================================

if __name__ == "__main__":
    """Test tool assembly"""
    print("="*60)
    print("TOOLS ASSEMBLY TEST")
    print("="*60)
    print()
    
    try:
        # Get all tools
        tools = get_all_tools()
        
        # Display tool details
        print(" AVAILABLE TOOLS:")
        for i, tool in enumerate(tools, 1):
            print(f"\n   {i}. {tool.name}")
            # Show first 100 chars of description
            desc = tool.description.strip().split('\n')[0][:100]
            print(f"      {desc}...")
        
        print()
        print(" TOOLS ASSEMBLY TEST PASSED")
        print()
        
    except Exception as e:
        print(f" TOOLS ASSEMBLY TEST FAILED")
        print(f"   Error: {str(e)}")
        print()
        print(" Make sure server.py is running:")
        print("   python server.py")
        print()