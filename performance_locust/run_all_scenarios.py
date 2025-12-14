#!/usr/bin/env python
"""
Automated Multi-Scenario Performance Test Runner
=================================================
This script automatically runs all 4 test scenarios sequentially with hardcoded durations.

Usage:
    python run_all_scenarios.py

This will run:
  1. Baseline: 10 users, 5 minutes
  2. Normal: 50 users, 5 minutes  
  3. Peak: 100 users, 5 minutes
  4. Stress: 200 users, 5 minutes

Total runtime: ~25 minutes (including cooldown periods)
"""

import subprocess
import time
from datetime import datetime
import os

# Configuration
HOST = "http://136.119.54.74:8080"
RESULTS_DIR = "results"
TEST_FILE = "comprehensive_system_test.py"

# Test scenarios with hardcoded parameters
SCENARIOS = [
    {
        "name": "scenario1_baseline",
        "description": "Baseline - Light Load (10 users)",
        "users": 10,
        "spawn_rate": 2,
        "duration": "5m"
    },
    {
        "name": "scenario2_normal",
        "description": "Normal Operations (50 users)",
        "users": 50,
        "spawn_rate": 5,
        "duration": "5m"
    },
    {
        "name": "scenario3_peak",
        "description": "Peak Hours - High Load (100 users)",
        "users": 100,
        "spawn_rate": 10,
        "duration": "5m"
    },
    {
        "name": "scenario4_stress",
        "description": "Stress Test - Maximum Load (200 users)",
        "users": 200,
        "spawn_rate": 20,
        "duration": "5m"
    }
]

# ANSI color codes for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*80}{Colors.RESET}\n")


def print_scenario_start(scenario_num, total, scenario):
    """Print scenario start information"""
    print(f"\n{Colors.YELLOW}{'─'*80}{Colors.RESET}")
    print(f"{Colors.YELLOW}RUNNING SCENARIO {scenario_num}/{total}: {scenario['description']}{Colors.RESET}")
    print(f"{Colors.YELLOW}{'─'*80}{Colors.RESET}")
    print(f"  Users:       {scenario['users']}")
    print(f"  Spawn Rate:  {scenario['spawn_rate']} users/second")
    print(f"  Duration:    {scenario['duration']}")
    print()


def print_scenario_complete(scenario_num, total):
    """Print scenario completion"""
    print(f"\n{Colors.GREEN}✓ Scenario {scenario_num}/{total} completed{Colors.RESET}")


def run_scenario(scenario, scenario_num, total_scenarios, timestamp):
    """Run a single test scenario"""
    
    print_scenario_start(scenario_num, total_scenarios, scenario)
    
    # Build output file paths
    html_output = f"{RESULTS_DIR}/{scenario['name']}_{timestamp}.html"
    csv_output = f"{RESULTS_DIR}/{scenario['name']}_{timestamp}"
    
    # Build locust command
    cmd = [
        "locust",
        "-f", TEST_FILE,
        "--host", HOST,
        "--users", str(scenario["users"]),
        "--spawn-rate", str(scenario["spawn_rate"]),
        "--run-time", scenario["duration"],
        "--headless",
        "--html", html_output,
        "--csv", csv_output,
        "--loglevel", "INFO"
    ]
    
    print(f"{Colors.BLUE}Command: {' '.join(cmd)}{Colors.RESET}\n")
    
    # Run the test
    try:
        result = subprocess.run(cmd, check=True)
        print_scenario_complete(scenario_num, total_scenarios)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{Colors.RED}✗ Scenario {scenario_num} failed with error code {e.returncode}{Colors.RESET}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Test interrupted by user{Colors.RESET}")
        return False


def main():
    """Main execution function"""
    
    # Create results directory
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Generate timestamp for this test run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print_header("MARTIAN BANK - COMPREHENSIVE PERFORMANCE TEST SUITE")
    print(f"Host:             {HOST}")
    print(f"Test File:        {TEST_FILE}")
    print(f"Results Directory: {RESULTS_DIR}")
    print(f"Timestamp:        {timestamp}")
    print(f"Total Scenarios:  {len(SCENARIOS)}")
    print()
    
    # Track results
    results = []
    start_time = time.time()
    
    # Run each scenario
    for i, scenario in enumerate(SCENARIOS, start=1):
        scenario_start = time.time()
        
        success = run_scenario(scenario, i, len(SCENARIOS), timestamp)
        results.append({
            "scenario": scenario["name"],
            "success": success,
            "duration": time.time() - scenario_start
        })
        
        # Cooldown between scenarios (except after last one)
        if i < len(SCENARIOS):
            cooldown = 30
            print(f"\n{Colors.YELLOW}Waiting {cooldown} seconds before next scenario (cooldown period)...{Colors.RESET}")
            time.sleep(cooldown)
    
    # Print final summary
    total_time = time.time() - start_time
    
    print_header("TEST SUITE COMPLETE")
    print(f"Total Runtime: {total_time/60:.1f} minutes ({total_time:.0f} seconds)\n")
    
    print(f"{Colors.BOLD}Results Summary:{Colors.RESET}")
    for i, result in enumerate(results, start=1):
        status = f"{Colors.GREEN}✓ PASSED{Colors.RESET}" if result["success"] else f"{Colors.RED}✗ FAILED{Colors.RESET}"
        print(f"  {i}. {result['scenario']}: {status} ({result['duration']/60:.1f} min)")
    
    print(f"\n{Colors.BOLD}Generated Reports:{Colors.RESET}")
    print(f"  Location: {RESULTS_DIR}/")
    print(f"  Pattern:  *_{timestamp}.*")
    
    print(f"\n{Colors.YELLOW}Next Steps:{Colors.RESET}")
    print("  1. Review HTML reports in the results directory")
    print("  2. Analyze CSV files for detailed metrics")
    print("  3. Check GCP Console for infrastructure metrics:")
    print("     - GKE pod scaling (HPA behavior)")
    print("     - Cloud Function invocations and latency")
    print("     - MongoDB VM resource utilization")
    print("     - Load balancer request rates and errors")
    print()
    
    # Return success if all scenarios passed
    all_passed = all(r["success"] for r in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Test suite interrupted by user{Colors.RESET}")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        exit(1)
