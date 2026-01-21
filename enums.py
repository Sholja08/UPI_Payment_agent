from enum import Enum

class Tool(str, Enum):
    OUTPUT = "output"
    ERROR_HANDLER = "error_handler"
    GET_TRANSACTION_DETAILS = "get_transaction_details"
    # GET_FAILURE_REASON = "get_failure_reason" 
