import sqlite3
from typing import Dict, Any
from .db_utils import get_db_connection, row_to_dict

def get_customer(customer_id: int) -> Dict[str, Any]:
    """
    Retrieve a specific customer by ID.
    
    Args:
        customer_id: The unique ID of the customer (This comes from the user 
        and it is the id of the customer) - cant be null
        
    Returns:
        Dict containing customer data or error message (success: True/False, error: str)
    """
    try:
        conn = get_db_connection()  # this is the connection to the database, cant be null
        cursor = conn.cursor()  # this is the pointer to the database, cant be null, we use it to execute queries
        
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()  # this is the row of the customer
        conn.close() #close the connection to the database
        
        if row: #if the customer is found
            return { #return the customer data
                'success': True,
                'customer': row_to_dict(row) #convert the row to a dictionary
            }
        else:
            return { #return the error message
                'success': False,
                'error': f'Customer with ID {customer_id} not found' #error message
            }
    except Exception as e:
        return { #return the error message, couldnt setup the connection to the database
            'success': False,
            'error': f'Database error: {str(e)}' #error message 
        }
