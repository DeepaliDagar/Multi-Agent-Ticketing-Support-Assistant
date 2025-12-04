import sqlite3
from typing import Dict, Any, Optional
from .db_utils import get_db_connection, row_to_dict

def list_customers(status: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Retrieve a list of customers.
    If status is provided, return only customers with that status.
    If limit is provided, return only the number of customers specified.
    
    Args:
        status: The status of the customers (active, disabled) - optional
        limit: The number of customers to return - optional
        
    Returns:
        Dict containing list of customers with name, email, phone
    """
    try:
        conn = get_db_connection()  
        cursor = conn.cursor() 
        
        # Build query based on whether status filter is provided
        if status:
            if limit:
                cursor.execute(
                    'SELECT name, email, phone FROM customers WHERE status = ? ORDER BY name LIMIT ?', 
                    (status, limit)
                )
            else:
                cursor.execute(
                    'SELECT name, email, phone FROM customers WHERE status = ? ORDER BY name', 
                    (status,)
                )
        else:
            if limit:
                cursor.execute(
                    'SELECT name, email, phone FROM customers ORDER BY name LIMIT ?', 
                    (limit,)
                )
            else:
                cursor.execute('SELECT name, email, phone FROM customers ORDER BY name')
        
        rows = cursor.fetchall()  # Get ALL matching customers
        conn.close()
        
        # Convert all rows to list of dicts
        customers = [row_to_dict(row) for row in rows]
        
        return {
            'success': True,
            'customers': customers,
            'count': len(customers)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
