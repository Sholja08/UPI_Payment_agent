import json
import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("PaymentAgent")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "transactions.json")


def load_transactions():
    """Load transactions from JSON file"""
    try:
        print(f" Reading from: {JSON_PATH}")
        with open(JSON_PATH, 'r') as f:
            data = json.load(f)
        print(f" Loaded {len(data)} transactions")
        return data
    except FileNotFoundError:
        print(f" Error: {JSON_PATH} not found")
        return []
    except json.JSONDecodeError as e:
        print(f" Error: Invalid JSON format - {str(e)}")
        return []


@mcp.tool()
def get_transaction_details(
    date: Optional[str] = None,
    time: Optional[str] = None,
    amount: Optional[float] = None,
    sender_last4: Optional[str] = None,
    last_n: int = 10,
    fuzzy_search: bool = True  # NEW: Enable fuzzy matching by default
):
    """
    Returns UPI transaction details based on filters.

    Parameters:
        date (Optional[str]): Transaction date in YYYY-MM-DD format.
        time (Optional[str]): Transaction time in HH:MM:SS format.
        amount (Optional[float]): Transaction amount.
        sender_last4 (Optional[str]): Last 4 digits of sender account number.
        last_n (int): Maximum number of results to return (default: 10).
        fuzzy_search (bool): If True, returns close matches when exact match fails.

    Output:
        {
            "success": <bool>,
            "count": <int>,
            "message": <str>,
            "transactions": [...],
            "fuzzy_matches": [...] (optional - only if fuzzy_search enabled)
        }
    """
    try:
        all_transactions = load_transactions()
        
        if not all_transactions:
            return {
                "success": False,
                "count": 0,
                "message": "No transactions found in database",
                "transactions": []
            }

        print(f"\n🔍 TRANSACTION SEARCH:")
        print(f"   Total transactions: {len(all_transactions)}")
        print(f"   Filters:")
        print(f"     - Date: {date}")
        print(f"     - Time: {time}")
        print(f"     - Amount: {amount}")
        print(f"     - Sender Last4: {sender_last4}")

        # EXACT MATCH SEARCH
        filtered = all_transactions.copy()

        if date:
            filtered = [txn for txn in filtered if txn.get('date') == date]
            print(f"   ✓ After date filter: {len(filtered)}")

        if sender_last4 and sender_last4 != "0000":
            filtered = [
                txn for txn in filtered 
                if txn.get('sender_last4') == sender_last4
            ]
            print(f"   ✓ After sender_last4 filter: {len(filtered)}")

        if time and time != "00:00:00":
            if len(time) == 5:
                time += ":00"

            try:
                user_time = datetime.strptime(time, "%H:%M:%S")

                def time_close(txn_time):
                    try:
                        txn_dt = datetime.strptime(txn_time, "%H:%M:%S")
                        time_diff = abs((txn_dt - user_time).total_seconds())
                        return time_diff <= 1800  # 30 minutes
                    except:
                        return False

                filtered = [
                    txn for txn in filtered
                    if txn.get("time") and time_close(txn["time"])
                ]
                print(f"   ✓ After time filter (±30 min): {len(filtered)}")
                            
            except Exception as e:
                print(f"    Time parsing error: {e}")

        if amount is not None and amount > 0:
            filtered = [
                txn for txn in filtered
                if abs(txn.get("amount", 0) - amount) <= 50
            ]
            print(f"   ✓ After amount filter (±50): {len(filtered)}")

        # Limit results
        filtered = filtered[:last_n]

        # FORMAT TRANSACTIONS
        def format_transaction(txn):
            return {
                "txn_id": txn.get('txn_id'),
                "date": txn.get('date'),
                "time": txn.get('time'),
                "amount": txn.get('amount'),
                "sender_last4": txn.get('sender_last4'),
                "receiver_account_no": txn.get('receiver_account_no'),
                "receiver_bank_name": txn.get('receiver_bank_name'),
                "sender_bank_name": txn.get('sender_bank_name'),
                "status": txn.get('status'),
                "description": txn.get('description'),
                "failure_reason": txn.get('failure_reason')
            }

        # IF EXACT MATCHES FOUND
        if filtered:
            print(f"   Returning {len(filtered)} exact match(es)\n")
            return {
                "success": True,
                "count": len(filtered),
                "message": f"Found {len(filtered)} transaction(s).",
                "transactions": [format_transaction(txn) for txn in filtered]
            }

        # IF NO EXACT MATCHES AND FUZZY SEARCH ENABLED
        if fuzzy_search:
            print(f"     No exact matches. Trying fuzzy search...")
            
            fuzzy_matches = []
            
            # Relaxed search: date + time + amount (ignore last4)
            if date and time and amount:
                user_time = datetime.strptime(time if len(time) == 8 else time + ":00", "%H:%M:%S")
                
                for txn in all_transactions:
                    if txn.get('date') != date:
                        continue
                    
                    # Check time (within 30 min)
                    try:
                        txn_time = datetime.strptime(txn.get('time', ''), "%H:%M:%S")
                        time_diff = abs((txn_time - user_time).total_seconds())
                        if time_diff > 1800:
                            continue
                    except:
                        continue
                    
                    # Check amount (within ±50)
                    if abs(txn.get('amount', 0) - amount) > 50:
                        continue
                    
                    # This is a fuzzy match!
                    fuzzy_matches.append(txn)
                
                if fuzzy_matches:
                    fuzzy_matches = fuzzy_matches[:last_n]
                    print(f"    Found {len(fuzzy_matches)} fuzzy match(es) (ignoring last4)\n")
                    
                    return {
                        "success": True,
                        "count": len(fuzzy_matches),
                        "message": f"No exact match found, but found {len(fuzzy_matches)} transaction(s) with matching date, time, and amount. The last 4 digits might be different - please verify.",
                        "transactions": [format_transaction(txn) for txn in fuzzy_matches],
                        "warning": "Account number last 4 digits don't match. Please verify your account details."
                    }

        # NO MATCHES AT ALL
        print(f"   No matches found\n")
        
        # Provide helpful debugging info
        debug_info = []
        if date:
            date_matches = [t for t in all_transactions if t.get('date') == date]
            debug_info.append(f"{len(date_matches)} transactions on {date}")
        
        return {
            "success": False,
            "count": 0,
            "message": "No transactions found matching the criteria.",
            "transactions": [],
            "debug_info": " | ".join(debug_info) if debug_info else "No transactions found in database for this date"
        }

    except Exception as e:
        print(f"Error in get_transaction_details: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "count": 0,
            "message": f"Database error: {str(e)}",
            "transactions": []
        }


if __name__ == "__main__":
    print("="*60)
    print(" PAYMENT AGENT MCP SERVER (Enhanced with Fuzzy Matching)")
    print("="*60)
    print(f" JSON File Path: {JSON_PATH}")
    
    if os.path.exists(JSON_PATH):
        transactions = load_transactions()
       
    else:
        print(f"  WARNING: {JSON_PATH} not found!")
        print(f"   Please ensure transactions.json exists")
    
    print(" Server starting on: http://localhost:8000/mcp")
    print()
    
    mcp.run(transport="streamable-http")
