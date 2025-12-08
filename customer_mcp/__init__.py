





# Define the tools that will be exposed via MCP
MCP_TOOLS = [
    {
        "name":"get_customer",
        "description":"Retrieve complete customer details by ID including name, email, phone, status, and timestamps",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The unique ID of the customer"
                }
            },
            "required": ["customer_id"]
        }
    },
    {
        "name":"get_customer_history",
        "description":"Get all support tickets associated with a customer by their ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "integer", "description": "The unique ID of the customer"}
            },
            "required": ["customer_id"]
        }
    },
    {
        "name":"list_customers",
        "description":"List customers with optional filtering by status and limit on number of results",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "description": "Filter by customer status (optional)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of customers to return (optional)"
                }
            }
        }
    },
    {
        "name":"add_customer",
        "description":"Create a new customer with name (required) and optional email, phone, and status",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Customer name (required)"
                },
                "email": {
                    "type": "string",
                    "description": "Customer email address (optional)"
                },
                "phone": {
                    "type": "string",
                    "description": "Customer phone number (optional)"
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "description": "Customer status (optional, defaults to 'active')"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name":"update_customer",
        "description":"Update customer information (name, email, phone, or status) by customer ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The unique ID of the customer to update"
                },
                "name": {
                    "type": "string",
                    "description": "New customer name (optional)"
                },
                "email": {
                    "type": "string",
                    "description": "New email address (optional)"
                },
                "phone": {
                    "type": "string",
                    "description": "New phone number (optional)"
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "disabled"],
                    "description": "New status (optional)"
                }
            },
            "required": ["customer_id"]
        }
    },
        {
        "name":"create_ticket",
        "description":"Create a new ticket for a customer by their ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "integer",
                    "description": "The unique ID of the customer"
                },
                "issue": {
                    "type": "string",
                    "description": "The issue of the ticket"
                },
                "priority": {
                    "type": "string",
                    "description": "The priority of the ticket"
                }
            },
            "required": ["customer_id", "issue", "priority"]
        }
    },
    {
        "name":"fallback_sql",
        "description":"Execute a SQL query. Supports SELECT, INSERT, and UPDATE operations only",
        "input_schema": {
            "type": "object",
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "SQL query to execute (SELECT, INSERT, or UPDATE only)"
                }
            },
            "required": ["sql_query"]
        }
    }
]

