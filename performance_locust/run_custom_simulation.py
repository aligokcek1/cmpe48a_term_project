#!/usr/bin/env python
"""
Martian Bank - Custom Performance Simulation
=============================================
Interactive script to run performance tests with custom parameters.

This script simulates realistic user behavior across all Martian Bank components
with configurable metrics for testing different scenarios.

Usage:
    # Interactive mode (prompts for parameters)
    python run_custom_simulation.py

    # Command-line mode (specify all parameters)
    python run_custom_simulation.py --users 50 --spawn-rate 5 --duration 10m --name my_test

Components tested:
    - Authentication Service (Registration, Login, Logout)
    - Account Management (Create, View, Get Details)
    - Transactions (Internal/External Transfers, History)
    - Loan Services (Application, History - Cloud Functions)
    - ATM Locator (Search - Cloud Function)
    - MongoDB VM (Database operations)
    - NGINX Load Balancer (Request routing)
    - GKE Kubernetes (HPA auto-scaling)
"""

import argparse
import subprocess
import sys
import os
from datetime import datetime
import re

# ANSI color codes
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}\n")


def print_section(text):
    """Print section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─'*len(text)}{Colors.RESET}")


def validate_duration(duration_str):
    """Validate duration format (e.g., '10m', '300s', '1h')"""
    pattern = r'^\d+[smh]$'
    if re.match(pattern, duration_str):
        return True
    return False


def get_user_input_interactive():
    """Prompt user for test parameters interactively"""
    
    print_header("MARTIAN BANK - CUSTOM PERFORMANCE SIMULATION")
    
    print(f"{Colors.YELLOW}Configure your performance test parameters:{Colors.RESET}\n")
    
    # Test name
    print_section("Test Identification")
    test_name = input(f"{Colors.GREEN}Test name{Colors.RESET} (e.g., 'peak_hour_test'): ").strip()
    if not test_name:
        test_name = f"custom_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"  → Using default: {test_name}")
    
    # Number of users
    print_section("Concurrent Users")
    print("  Examples: 10 (light), 50 (normal), 100 (peak), 200+ (stress)")
    while True:
        users_input = input(f"{Colors.GREEN}Number of concurrent users{Colors.RESET} [default: 50]: ").strip()
        if not users_input:
            users = 50
            break
        try:
            users = int(users_input)
            if users <= 0:
                print(f"  {Colors.RED}✗ Must be positive{Colors.RESET}")
                continue
            if users > 1000:
                confirm = input(f"  {Colors.YELLOW}⚠ {users} users is very high. Continue? (y/n):{Colors.RESET} ")
                if confirm.lower() != 'y':
                    continue
            break
        except ValueError:
            print(f"  {Colors.RED}✗ Invalid number{Colors.RESET}")
    
    # Spawn rate
    print_section("Spawn Rate (Users per Second)")
    print("  Examples: 1-2 (gradual), 5-10 (normal), 20+ (rapid)")
    while True:
        spawn_input = input(f"{Colors.GREEN}Users to spawn per second{Colors.RESET} [default: 5]: ").strip()
        if not spawn_input:
            spawn_rate = 5
            break
        try:
            spawn_rate = int(spawn_input)
            if spawn_rate <= 0:
                print(f"  {Colors.RED}✗ Must be positive{Colors.RESET}")
                continue
            if spawn_rate > users:
                print(f"  {Colors.YELLOW}⚠ Spawn rate higher than total users, adjusting to {users}{Colors.RESET}")
                spawn_rate = users
            break
        except ValueError:
            print(f"  {Colors.RED}✗ Invalid number{Colors.RESET}")
    
    # Duration
    print_section("Test Duration")
    print("  Format: <number><unit> where unit is s(econds), m(inutes), or h(ours)")
    print("  Examples: 5m, 300s, 1h")
    while True:
        duration = input(f"{Colors.GREEN}Test duration{Colors.RESET} [default: 5m]: ").strip()
        if not duration:
            duration = "5m"
            break
        if validate_duration(duration):
            break
        print(f"  {Colors.RED}✗ Invalid format. Use: 10m, 300s, or 1h{Colors.RESET}")
    
    # Output format
    print_section("Output Options")
    print("  HTML report: Visual charts and statistics")
    print("  CSV data: Raw data for analysis")
    generate_html = input(f"{Colors.GREEN}Generate HTML report?{Colors.RESET} [Y/n]: ").strip().lower() != 'n'
    generate_csv = input(f"{Colors.GREEN}Generate CSV data?{Colors.RESET} [Y/n]: ").strip().lower() != 'n'
    
    # Advanced options
    print_section("Advanced Options (Optional)")
    show_advanced = input(f"{Colors.GREEN}Configure advanced options?{Colors.RESET} [y/N]: ").strip().lower() == 'y'
    
    advanced = {
        "headless": True,
        "loglevel": "INFO"
    }
    
    if show_advanced:
        # Headless mode
        headless_input = input(f"  Run in headless mode (no web UI)? [Y/n]: ").strip().lower()
        advanced["headless"] = headless_input != 'n'
        
        # Log level
        print("  Log levels: DEBUG, INFO, WARNING, ERROR")
        loglevel_input = input(f"  Log level [INFO]: ").strip().upper()
        if loglevel_input in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            advanced["loglevel"] = loglevel_input
        else:
            advanced["loglevel"] = "INFO"
    
    return {
        "test_name": test_name,
        "users": users,
        "spawn_rate": spawn_rate,
        "duration": duration,
        "generate_html": generate_html,
        "generate_csv": generate_csv,
        "headless": advanced["headless"],
        "loglevel": advanced["loglevel"]
    }


def print_test_summary(params):
    """Display test configuration summary"""
    print_header("TEST CONFIGURATION SUMMARY")
    
    print(f"{Colors.BOLD}Test Details:{Colors.RESET}")
    print(f"  Test Name:        {Colors.CYAN}{params['test_name']}{Colors.RESET}")
    print(f"  Concurrent Users: {Colors.CYAN}{params['users']}{Colors.RESET}")
    print(f"  Spawn Rate:       {Colors.CYAN}{params['spawn_rate']} users/second{Colors.RESET}")
    print(f"  Duration:         {Colors.CYAN}{params['duration']}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Output Options:{Colors.RESET}")
    print(f"  HTML Report:      {Colors.GREEN}Yes{Colors.RESET}" if params['generate_html'] else f"  HTML Report:      {Colors.YELLOW}No{Colors.RESET}")
    print(f"  CSV Data:         {Colors.GREEN}Yes{Colors.RESET}" if params['generate_csv'] else f"  CSV Data:         {Colors.YELLOW}No{Colors.RESET}")
    print(f"  Headless Mode:    {Colors.GREEN}Yes{Colors.RESET}" if params['headless'] else f"  Headless Mode:    {Colors.YELLOW}No{Colors.RESET}")
    print(f"  Log Level:        {Colors.CYAN}{params['loglevel']}{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}Test Scope:{Colors.RESET}")
    print(f"  ✓ Authentication Service (Registration, Login, Logout)")
    print(f"  ✓ Account Management (Create, View, Details)")
    print(f"  ✓ Transaction Processing (Internal/External Transfers, History)")
    print(f"  ✓ Loan Services (Application, History) - Cloud Functions")
    print(f"  ✓ ATM Locator - Cloud Function")
    print(f"  ✓ NGINX Load Balancer")
    print(f"  ✓ MongoDB Database")
    print(f"  ✓ Kubernetes HPA Auto-scaling")
    
    # Calculate estimated metrics
    ramp_up_time = params['users'] / params['spawn_rate']
    print(f"\n{Colors.BOLD}Expected Behavior:{Colors.RESET}")
    print(f"  Ramp-up Time:     ~{ramp_up_time:.0f} seconds")
    
    if params['users'] <= 20:
        load_category = "Light Load"
        expectation = "Minimal resource usage, no scaling expected"
    elif params['users'] <= 60:
        load_category = "Normal Load"
        expectation = "Stable performance, possible minimal HPA scaling"
    elif params['users'] <= 120:
        load_category = "High Load"
        expectation = "HPA scaling expected, increased latency acceptable"
    else:
        load_category = "Stress Test"
        expectation = "Aggressive scaling, some errors may occur"
    
    print(f"  Load Category:    {Colors.CYAN}{load_category}{Colors.RESET}")
    print(f"  Expectation:      {expectation}")


def run_test(params):
    """Execute the performance test with given parameters"""
    
    # Create results directory
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Build file paths
    test_file = "comprehensive_system_test.py"
    host = "http://136.119.54.74:8080"
    
    html_output = f"{results_dir}/{params['test_name']}_{timestamp}.html" if params['generate_html'] else None
    csv_output = f"{results_dir}/{params['test_name']}_{timestamp}" if params['generate_csv'] else None
    
    # Build locust command
    cmd = [
        "locust",
        "-f", test_file,
        "--host", host,
        "--users", str(params['users']),
        "--spawn-rate", str(params['spawn_rate']),
        "--run-time", params['duration'],
        "--loglevel", params['loglevel']
    ]
    
    if params['headless']:
        cmd.append("--headless")
    
    if html_output:
        cmd.extend(["--html", html_output])
    
    if csv_output:
        cmd.extend(["--csv", csv_output])
    
    # Display command
    print(f"\n{Colors.BOLD}Executing Command:{Colors.RESET}")
    print(f"{Colors.CYAN}{' '.join(cmd)}{Colors.RESET}\n")
    
    print_header("TEST EXECUTION STARTED")
    print(f"{Colors.YELLOW}Press Ctrl+C to stop the test early{Colors.RESET}\n")
    
    # Execute test
    try:
        start_time = datetime.now()
        result = subprocess.run(cmd, check=True)
        end_time = datetime.now()
        
        print_header("TEST COMPLETED SUCCESSFULLY")
        print(f"Duration: {(end_time - start_time).total_seconds():.0f} seconds\n")
        
        if html_output:
            print(f"{Colors.GREEN}✓ HTML Report:{Colors.RESET} {html_output}")
        if csv_output:
            print(f"{Colors.GREEN}✓ CSV Data:{Colors.RESET} {csv_output}_*.csv")
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        print(f"  1. Review the HTML report for visualizations and statistics")
        print(f"  2. Analyze CSV data for detailed metrics")
        print(f"  3. Check GCP Console for infrastructure metrics:")
        print(f"     • GKE Workloads: Kubernetes Engine → Workloads")
        print(f"     • Cloud Functions: Cloud Functions → Metrics")
        print(f"     • MongoDB VM: Compute Engine → mongodb-vm → Monitoring")
        print(f"     • Load Balancer: Network Services → Load balancing")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n{Colors.RED}✗ Test failed with exit code {e.returncode}{Colors.RESET}")
        return False
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
        return False


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Run custom performance simulation for Martian Bank",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python run_custom_simulation.py

  # Light load test
  python run_custom_simulation.py --users 10 --spawn-rate 2 --duration 5m --name light_test

  # Normal load test
  python run_custom_simulation.py --users 50 --spawn-rate 5 --duration 10m --name normal_test

  # Peak load test
  python run_custom_simulation.py --users 100 --spawn-rate 10 --duration 15m --name peak_test

  # Stress test
  python run_custom_simulation.py --users 200 --spawn-rate 20 --duration 20m --name stress_test

  # Quick test without HTML
  python run_custom_simulation.py --users 20 --duration 2m --no-html
        """
    )
    
    parser.add_argument('--users', '-u', type=int, help='Number of concurrent users')
    parser.add_argument('--spawn-rate', '-r', type=int, help='Users to spawn per second')
    parser.add_argument('--duration', '-d', type=str, help='Test duration (e.g., 5m, 300s, 1h)')
    parser.add_argument('--name', '-n', type=str, help='Test name for output files')
    parser.add_argument('--no-html', action='store_true', help='Skip HTML report generation')
    parser.add_argument('--no-csv', action='store_true', help='Skip CSV data generation')
    parser.add_argument('--no-headless', action='store_true', help='Run with web UI (not headless)')
    parser.add_argument('--loglevel', '-l', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Log level')
    
    return parser.parse_args()


def main():
    """Main execution function"""
    
    args = parse_args()
    
    # Determine if running in interactive or CLI mode
    if args.users is None:
        # Interactive mode
        params = get_user_input_interactive()
    else:
        # CLI mode - validate required parameters
        if args.spawn_rate is None:
            print(f"{Colors.RED}Error: --spawn-rate is required when using --users{Colors.RESET}")
            sys.exit(1)
        if args.duration is None:
            print(f"{Colors.RED}Error: --duration is required when using --users{Colors.RESET}")
            sys.exit(1)
        
        if not validate_duration(args.duration):
            print(f"{Colors.RED}Error: Invalid duration format. Use: 10m, 300s, or 1h{Colors.RESET}")
            sys.exit(1)
        
        params = {
            "test_name": args.name or f"custom_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "users": args.users,
            "spawn_rate": args.spawn_rate,
            "duration": args.duration,
            "generate_html": not args.no_html,
            "generate_csv": not args.no_csv,
            "headless": not args.no_headless,
            "loglevel": args.loglevel
        }
    
    # Show summary
    print_test_summary(params)
    
    # Confirm execution
    print(f"\n{Colors.BOLD}Ready to start test?{Colors.RESET}")
    confirm = input(f"{Colors.GREEN}Press Enter to continue, or Ctrl+C to cancel...{Colors.RESET}")
    
    # Run test
    success = run_test(params)
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Operation cancelled by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
