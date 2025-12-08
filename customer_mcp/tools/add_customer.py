import sqlite3
from typing import Dict, Any, Optional
from .db_utils import get_db_connection, row_to_dict

def add_customer(name: str, email: Optional[str] = None, phone: Optional[str] = None, status: str = None) -> Dict[str, Any]:
    """
    Add a new customer to the database.
    #no need to assign it a status, it will be active by default
    #no need to assign it an id, it will be auto-incremented
    
    Args:
        name: Customer's full name (required)
        email: Customer's email address (optional)
        phone: Customer's phone number (optional)
        
    Returns:
        Dict containing the new customer data or error message
    """
    try:

        name = name.strip() if name else None
        email = email.strip() if email else None
        phone = phone.strip() if phone else None

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build INSERT dynamically based on provided fields
        # using status, incase we want to add a prev cusomer details (who's details are not in the database)
        if status:
            cursor.execute(
                'INSERT INTO customers (name, email, phone, status) VALUES (?, ?, ?, ?)',
                (name, email, phone, status)
            )
        else:
            # Let DB use default 'active' status
            cursor.execute(
                'INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)',
                (name, email, phone)
            )
        
        conn.commit()
        new_customer_id = cursor.lastrowid  # this is the id of the new customer (inbuilt function)
        
        # Fetch the complete new customer record
        cursor.execute('SELECT * FROM customers WHERE id = ?', (new_customer_id,))
        new_customer = cursor.fetchone()
        conn.close()
        
        return {
            'success': True,
            'message': f'Customer created successfully with ID {new_customer_id}',
            'customer': row_to_dict(new_customer)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }