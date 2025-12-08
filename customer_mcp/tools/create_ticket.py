import sqlite3
import time
from typing import Dict, Any, Optional
from .db_utils import get_db_connection, row_to_dict

def create_ticket(customer_id: int, issue: str, priority: str = 'medium') -> Dict[str, Any]:
    """
    Create a new ticket for a customer.
    
    Args:
        customer_id: Customer's ID (required)
        issue: The issue description (required)
        priority: The priority level - 'low', 'medium', or 'high' (optional, defaults to 'medium')
                 LLM should determine based on issue severity:
                 - high: login/access issues, account locked, payment failures, data loss
                 - medium: bugs, performance issues, billing questions
                 - low: feature requests, general questions, minor issues
    """
    # Input validation
    if customer_id is None:
        return {
            'success': False,
            'error': 'Customer ID is required'
        }
    if issue is None:
        return {
            'success': False,
            'error': 'Issue is required'
        }
    
    # Validate priority value
    if priority not in ['low', 'medium', 'high']:
        priority = 'medium'  # Default to medium if invalid
    
    # Retry logic for database locks (rare with WAL mode)
    max_retries = 2
    retry_delay = 0.1  # seconds
    
    for attempt in range(max_retries):
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # check if the customer exists
            cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
            customer = cursor.fetchone()
            if customer is None:
                if conn:
                    conn.close()
                return {
                    'success': False,
                    'error': 'Customer not found'
                }
            
            cursor.execute(
                'INSERT INTO tickets (customer_id, issue, priority) VALUES (?, ?, ?)',
                (customer_id, issue, priority)
            )
            
            conn.commit()
            new_ticket_id = cursor.lastrowid  # this is the id of the new ticket (inbuilt function)
            
            # Fetch the complete new ticket record
            cursor.execute('SELECT * FROM tickets WHERE id = ?', (new_ticket_id,))
            new_ticket = cursor.fetchone() # this is the row of the new ticket
            conn.close()
            
            return {
                'success': True,
                'message': f'Ticket created successfully with ID {new_ticket_id}',
                'ticket': row_to_dict(new_ticket)
            }
            
        except sqlite3.OperationalError as e:
            if conn:
                conn.close()
            if 'locked' in str(e).lower() and attempt < max_retries - 1:
                # Database is locked, retry after a delay
                time.sleep(retry_delay)
                continue
            else:
                return {
                    'success': False,
                    'error': f'Database locked error: {str(e)}. Please try again in a moment.'
                }
        except Exception as e:
            if conn:
                conn.close()
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }
    
    return {
        'success': False,
        'error': 'Failed to create ticket after multiple retries. Database may be busy.'
    }