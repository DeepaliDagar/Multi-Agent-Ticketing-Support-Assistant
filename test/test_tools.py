"""
Test script to verify all MCP tools work correctly.
Run from project root: python test/test_tools.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from customer_mcp.tools.get_customer import get_customer
from customer_mcp.tools.get_customer_history import get_customer_history
from customer_mcp.tools.list_customers import list_customers
from customer_mcp.tools.add_customer import add_customer
from customer_mcp.tools.update_customer import update_customer
from customer_mcp.tools.fallback_sql import fallback_sql as execute_generated_sql

def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(result):
    """Pretty print a result dictionary."""
    if result.get('success'):
        print("✅ SUCCESS")
        for key, value in result.items():
            if key != 'success':
                print(f"  {key}: {value}")
    else:
        print("❌ FAILED")
        print(f"  Error: {result.get('error')}")
    print()

# =================================================================
# TEST 1: Get Customer
# =================================================================
print_header("TEST 1: Get Customer by ID")
print("Fetching customer with ID 1...")
result = get_customer(1)
print_result(result)

# =================================================================
# TEST 2: List All Customers
# =================================================================
print_header("TEST 2: List All Customers (Limit 5)")
print("Listing first 5 customers...")
result = list_customers(limit=5)
print_result(result)

# =================================================================
# TEST 3: List Customers by Status
# =================================================================
print_header("TEST 3: List Active Customers")
print("Filtering customers by status='active'...")
result = list_customers(status='active', limit=3)
print_result(result)

# =================================================================
# TEST 4: Add New Customer
# =================================================================
print_header("TEST 4: Add New Customer")
print("Adding 'Test User'...")
result = add_customer(
    name="Test User",
    email="test@example.com",
    phone="+1-555-TEST"
)
print_result(result)

# Store the new customer ID for update test
new_customer_id = result.get('customer', {}).get('id') if result.get('success') else None

# =================================================================
# TEST 5: Update Customer
# =================================================================
if new_customer_id:
    print_header("TEST 5: Update Customer")
    print(f"Updating customer ID {new_customer_id}...")
    result = update_customer(
        customer_id=new_customer_id,
        name="Test User Updated",
        email="updated@example.com"
    )
    print_result(result)
else:
    print_header("TEST 5: Update Customer")
    print("⚠️  SKIPPED - No customer ID from previous test")

# =================================================================
# TEST 6: Test SQL Fallback (if available)
# =================================================================
print_header("TEST 6: SQL Fallback - Direct Query")
print("Running: SELECT name, email FROM customers LIMIT 3")
try:
    result = execute_generated_sql("SELECT name, email FROM customers LIMIT 3")
    print_result(result)
except Exception as e:
    print(f"⚠️  Error: {str(e)}\n")

# =================================================================
# TEST 7: Error Handling - Invalid Customer ID
# =================================================================
print_header("TEST 7: Error Handling - Invalid ID")
print("Attempting to get customer with ID 99999...")
result = get_customer(99999)
print_result(result)

# =================================================================
# TEST 8: Error Handling - Empty Name
# =================================================================
print_header("TEST 8: Error Handling - Empty Name")
print("Attempting to add customer with empty name...")
result = add_customer(name="   ")
print_result(result)

# =================================================================
# SUMMARY
# =================================================================
print_header("TEST COMPLETE")
print("All manual tests finished!")
print("Review the results above to ensure all tools work correctly.")
print("="*60 + "\n")