import sqlite3
from typing import Dict, Any
from .db_utils import get_db_connection, row_to_dict

def update_customer(customer_id: int, name: str = None, email: str = None, 
                   phone: str = None, status: str = None) -> Dict[str, Any]:
    """
    Update customer information.
    
    Args:
        customer_id: ID of customer to update (required)
        name: New name (optional)
        email: New email (optional)
        phone: New phone (optional)
        status: New status - 'active' or 'disabled' (optional)
    
    Returns:
        Dict with success status, message, and UPDATED customer data
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build UPDATE query dynamically, so we can update any field we want
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        if email:
            updates.append("email = ?")
            params.append(email)
        if phone:
            updates.append("phone = ?")
            params.append(phone)
        if status:
            updates.append("status = ?")
            params.append(status)
        
        if not updates:
            return {
                'success': False,
                'error': 'No fields provided to update'
            }
        
        # Add customer_id to params
        params.append(customer_id)
        
        # Execute UPDATE
        query = f"UPDATE customers SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, tuple(params))
        conn.commit()
        
        if cursor.rowcount == 0:
            conn.close()
            return {
                'success': False,
                'error': f'Customer with ID {customer_id} not found'
            }
        
        # Get the updated data
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        updated_row = cursor.fetchone()
        conn.close()
        
        return {
            'success': True,
            'message': f'Customer {customer_id} updated successfully',
            'customer': row_to_dict(updated_row)  # Return updated data 
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }