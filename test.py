"""
Test script for A2A Multi-Agent System
Reflects scenarios from demo.ipynb
"""
import asyncio
import sys
import argparse
import html
from pathlib import Path
from datetime import datetime
from termcolor import colored

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import orchestrator
from a2a.orchestrator import A2AOrchestrator

# Handoff tracking
handoff_log = []
html_mode = False
html_output = []

def handoff_callback(event_type, data):
    """Track agent handoffs for summary."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if event_type == 'routing':
        handoff_log.append({
            'time': timestamp,
            'type': 'routing',
            'query': data.get('query', ''),
            'decision': data.get('decision', {})
        })
        decision = data.get('decision', {})
        agent = decision.get('next_agent', 'Unknown')
        reason = decision.get('reason', '')
        if not html_mode:
            print(colored(f"  [{timestamp}] 🔀 Routing to: ", "cyan") + colored(f"{agent.replace('_', ' ').title()} Agent", "cyan", attrs=["bold"]))
            print(colored(f"     Reason: ", "yellow") + colored(f"{reason}", "yellow"))
    elif event_type == 'handoff':
        from_agent = data.get('from_agent', '')
        to_agent = data.get('to_agent', '')
        handoff_log.append({
            'time': timestamp,
            'type': 'handoff',
            'from': from_agent,
            'to': to_agent,
            'reason': data.get('reason', '')
        })
        if not html_mode:
            print(colored(f"  [{timestamp}] 🔄 Handoff: ", "magenta") + 
                  colored(f"{from_agent or 'Start'}", "magenta") + 
                  colored(" → ", "magenta") + 
                  colored(f"{to_agent}", "magenta", attrs=["bold"]))
    elif event_type == 'agent_complete':
        agent = data.get('agent', '')
        handoff_log.append({
            'time': timestamp,
            'type': 'complete',
            'agent': agent
        })
        if not html_mode:
            print(colored(f"  [{timestamp}] ✅ {agent.replace('_', ' ').title()} Agent completed", "green"))
    elif event_type == 'completion':
        handoff_log.append({
            'time': timestamp,
            'type': 'done',
            'iteration': data.get('iteration', 0)
        })

def print_section(title, char="=", html_mode=False):
    """Print a formatted section header."""
    if html_mode:
        html_output.append(f'<h2 style="color: #0080ff; border-bottom: 2px solid #0080ff; padding: 10px 0;">{title}</h2>')
    else:
        print(colored(f"\n{char * 80}", "cyan"))
        print(colored(f"{title}", "cyan", attrs=["bold"]))
        print(colored(f"{char * 80}\n", "cyan"))

def print_query(query, scenario_num=None, html_mode=False):
    """Print user query in a formatted way."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if html_mode:
        escaped_query = html.escape(query)
        if scenario_num:
            html_output.append(f'<div style="background: #fff3cd; padding: 15px; margin: 10px 0; border-left: 4px solid #ffc107;"><h3>SCENARIO {scenario_num}</h3></div>')
        html_output.append(f'<div style="margin: 15px 0;"><strong style="color: #0066cc;">👤 User Query:</strong> <span style="color: #0066cc;">{escaped_query}</span></div>')
        html_output.append(f'<div style="margin: 5px 0; color: #666;">⏰ Time: {timestamp}</div>')
        html_output.append('<hr style="border: 1px solid #ccc;">')
    else:
        if scenario_num:
            print(colored(f"\n{'=' * 80}", "yellow"))
            print(colored(f"SCENARIO {scenario_num}", "yellow", attrs=["bold"]))
            print(colored(f"{'=' * 80}", "yellow"))
        print(colored(f"\n User Query: ", "blue", attrs=["bold"]) + colored(f"{query}", "blue"))
        print(colored(f" Time: ", "blue") + colored(f"{timestamp}", "yellow"))
        print(colored(f"\n{'-' * 80}", "cyan"))

def print_response(response, execution_time, html_mode=False):
    """Print agent response."""
    cleaned_response = response.replace("**", "").strip()
    if html_mode:
        html_output.append(f'<div style="background: #e8f5e9; padding: 15px; margin: 15px 0; border-left: 4px solid #4caf50;"><strong style="color: #2e7d32;">🤖 Agent Response:</strong></div>')
        escaped_response = html.escape(cleaned_response).replace('\n', '<br>')
        html_output.append(f'<div style="padding: 15px; margin: 10px 0; background: #f5f5f5; border-radius: 5px; white-space: pre-wrap; font-family: monospace;">{escaped_response}</div>')
        html_output.append(f'<div style="margin: 10px 0; color: #ff9800;">⏱ Execution Time: {execution_time:.2f} seconds</div>')
    else:
        print(colored(f"\n Agent Response:", "green", attrs=["bold"]))
        print(colored(f"{'-' * 80}", "cyan"))
        print(cleaned_response)
        print(colored(f"\n  Execution Time: {execution_time:.2f} seconds", "yellow"))

def print_handoff_summary(html_mode=False):
    """Print summary of agent handoffs."""
    if not handoff_log:
        return
    if html_mode:
        html_output.append('<div style="background: #e3f2fd; padding: 15px; margin: 15px 0; border-left: 4px solid #2196f3;"><strong style="color: #1976d2;">📊 A2A Coordination Summary:</strong></div>')
        html_output.append('<ul style="list-style: none; padding: 0;">')
        for i, log in enumerate(handoff_log, 1):
            if log['type'] == 'routing':
                agent = log['decision'].get('next_agent', 'Unknown')
                reason = log['decision'].get('reason', '')
                html_output.append(f'<li style="padding: 8px; margin: 5px 0; background: #f0f0f0; border-radius: 3px;">{i}. <span style="color: #00bcd4;">[{log["time"]}]</span> Routed to: <strong style="color: #00bcd4;">{agent.replace("_", " ").title()}</strong> - <span style="color: #ff9800;">{reason}</span></li>')
            elif log['type'] == 'complete':
                html_output.append(f'<li style="padding: 8px; margin: 5px 0; background: #e8f5e9; border-radius: 3px;">{i}. <span style="color: #4caf50;">[{log["time"]}]</span> <strong style="color: #4caf50;">{log["agent"].replace("_", " ").title()} completed</strong></li>')
        html_output.append('</ul>')
    else:
        print(colored(f"\n{'=' * 80}", "cyan"))
        print(colored(f"\n A2A Coordination Summary:", "green", attrs=["bold"]))
        print(colored(f"{'-' * 80}", "cyan"))
        for i, log in enumerate(handoff_log, 1):
            if log['type'] == 'routing':
                agent = log['decision'].get('next_agent', 'Unknown')
                reason = log['decision'].get('reason', '')
                print(colored(f"{i}. [{log['time']}] ", "cyan") + 
                      colored(f"Routed to: ", "cyan") + 
                      colored(f"{agent.replace('_', ' ').title()}", "cyan", attrs=["bold"]) + 
                      colored(f" - {reason}", "yellow"))
            elif log['type'] == 'complete':
                print(colored(f"{i}. [{log['time']}] ", "green") + 
                      colored(f"{log['agent'].replace('_', ' ').title()} completed", "green", attrs=["bold"]))

def run_scenario(scenario_num, query, description="", html_mode=False):
    """Run a single test scenario."""
    print_section(f"Scenario {scenario_num}", "=", html_mode)
    if html_mode:
        if description:
            html_output.append(f'<p style="color: #666; margin: 10px 0;"><em>{description}</em></p>')
    else:
        if description:
            print(colored(f"Description: {description}\n", "white"))
    
    print_query(query, scenario_num, html_mode)
    
    # Create orchestrator with handoff callback
    orchestrator = A2AOrchestrator(
        user_id="test_user",
        session_id=f"test_session_{scenario_num}",
        handoff_callback=handoff_callback
    )
    
    # Execute query
    start_time = datetime.now()
    try:
        response = asyncio.run(
            orchestrator.process_query(
                query,
                show_usage=False,
                silent=True
            )
        )
        execution_time = (datetime.now() - start_time).total_seconds()
        print_response(response, execution_time, html_mode)
        print_handoff_summary(html_mode)
        handoff_log.clear()
        return True
    except Exception as e:
        if html_mode:
            html_output.append(f'<div style="background: #ffebee; padding: 15px; margin: 10px 0; border-left: 4px solid #f44336;"><strong style="color: #c62828;">❌ Error:</strong> {str(e)}</div>')
            html_output.append('<p style="color: #ff6f00;">💡 Make sure MCP server is running: python customer_mcp/server/mcp_server.py</p>')
        else:
            print(colored(f"\n❌ Error: {str(e)}", "red"))
            print(colored("💡 Make sure MCP server is running: python customer_mcp/server/mcp_server.py", "yellow"))
        handoff_log.clear()
        return False

def generate_html(results, total, passed, failed):
    """Generate HTML output."""
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>A2A Multi-Agent System Test Results</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1976d2; border-bottom: 3px solid #1976d2; padding-bottom: 10px; }}
        .summary {{ background: #e3f2fd; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .summary-item {{ margin: 10px 0; font-size: 18px; }}
        .passed {{ color: #4caf50; font-weight: bold; }}
        .failed {{ color: #f44336; font-weight: bold; }}
        .total {{ color: #2196f3; font-weight: bold; }}
        .results-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .results-table th {{ background: #2196f3; color: white; padding: 12px; text-align: left; }}
        .results-table td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        .results-table tr:nth-child(even) {{ background: #f9f9f9; }}
        .status-pass {{ color: #4caf50; font-weight: bold; }}
        .status-fail {{ color: #f44336; font-weight: bold; }}
        code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <h1> A2A Multi-Agent System Test Suite</h1>
        <div class="summary">
            <div class="summary-item"><span class="total">Total Scenarios:</span> {total}</div>
            <div class="summary-item"><span class="passed">Passed:</span> {passed}</div>
            <div class="summary-item"><span class="failed">Failed:</span> {failed}</div>
        </div>
        <hr>
        {''.join(html_output)}
        <hr>
        <h2 style="color: #1976d2;">Test Summary</h2>
        <table class="results-table">
            <thead>
                <tr>
                    <th>Scenario</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>"""
    
    for num, success in results:
        status_class = "status-pass" if success else "status-fail"
        status_text = "✓ PASS" if success else "✗ FAIL"
        html += f'<tr><td>Scenario {num}</td><td class="{status_class}">{status_text}</td></tr>'
    
    html += """
            </tbody>
        </table>
        <hr>
        <p style="color: #666; text-align: center; margin-top: 30px;">
            Generated at: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
        </p>
    </div>
</body>
</html>"""
    return html

def main():
    """Run all test scenarios."""
    parser = argparse.ArgumentParser(description='Run A2A Multi-Agent System Tests')
    parser.add_argument('--html', action='store_true', help='Output results as HTML file')
    parser.add_argument('--output', type=str, default='test_results.html', help='HTML output filename')
    args = parser.parse_args()
    
    global html_mode
    html_mode = args.html
    
    if not html_mode:
        print(colored("\n" + "=" * 80, "cyan", attrs=["bold"]))
        print(colored("A2A Multi-Agent System Test Suite", "cyan", attrs=["bold"]))
        print(colored("=" * 80 + "\n", "cyan", attrs=["bold"]))
    else:
        html_output.append('<h1 style="color: #1976d2; border-bottom: 3px solid #1976d2; padding-bottom: 10px;">🚀 A2A Multi-Agent System Test Suite</h1>')
    
    scenarios = [
        {
            "num": 1,
            "query": "Get customer information for ID 5",
            "description": "Simple single-agent query"
        },
        {
            "num": 2,
            "query": "I need help with my account, customer ID 1",
            "description": "Task allocation - Customer support request"
        },
        {
            "num": 3,
            "query": "Get customer 1 and create a ticket for them with issue 'Cannot login'",
            "description": "Multi-step coordination"
        },
        {
            "num": 4,
            "query": "I'm customer 2, I've been charged twice, please help me",
            "description": "Negotiation/Escalation - Billing issues"
        },
        {
            "num": 5,
            "query": "Show me all active customers who have open tickets",
            "description": "Complex query - Multiple agents required"
        },
        {
            "num": 6,
            "query": "Get customer 3 and show me their ticket history",
            "description": "Multi-intent query - Parallel operations"
        },
        {
            "num": 7,
            "query": "Show me customers who created accounts last month",
            "description": "SQL Generator Agent - Complex analytics"
        },
        {
            "num": 8,
            "query": "I'm customer 1 and need help upgrading my account",
            "description": "Coordinated query - Account upgrade request"
        }
    ]
    
    results = []
    for scenario in scenarios:
        success = run_scenario(
            scenario["num"],
            scenario["query"],
            scenario["description"],
            html_mode
        )
        results.append((scenario["num"], success))
        if not html_mode:
            print("\n" + "=" * 80 + "\n")
        else:
            html_output.append('<hr style="margin: 30px 0; border: 2px solid #ccc;">')
    
    # Print summary
    passed = sum(1 for _, success in results if success)
    total = len(results)
    failed = total - passed
    
    if html_mode:
        html_content = generate_html(results, total, passed, failed)
        output_file = Path(args.output)
        output_file.write_text(html_content, encoding='utf-8')
        print(f"✅ HTML report generated: {output_file.absolute()}")
    else:
        print_section("Test Summary", "=")
        print(colored(f"Total Scenarios: {total}", "cyan"))
        print(colored(f"Passed: {passed}", "green"))
        print(colored(f"Failed: {failed}", "red" if failed > 0 else "green"))
        
        print("\nDetailed Results:")
        for num, success in results:
            status = colored("✓ PASS", "green") if success else colored("✗ FAIL", "red")
            print(f"  Scenario {num}: {status}")

if __name__ == "__main__":
    main()

