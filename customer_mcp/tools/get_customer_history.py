import sqlite3
from typing import Dict, Any
from .db_utils import get_db_connection, row_to_dict

def get_customer_history(customer_id: int) -> Dict[str, Any]:
    """
    Get the history of a customer by ID.
    
    Args:
        customer_id: The ID of the customer

    Returns:
        Dict containing the history of the customer or error message (success: True/False, error: str)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM tickets WHERE customer_id = ?', (customer_id,))
        rows = cursor.fetchall()
        conn.close()

        return {
            'success': True,
            'history': [row_to_dict(row) for row in rows]
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}' #error message
        }