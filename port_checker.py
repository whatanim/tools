import socket
import logging
import os
from contextlib import closing

# --- Configuration ---
HOST = '127.0.0.1'  # The IP address of the server to check (localhost for local checks)
PORTS_TCP = [22, 80, 443, 8080]
PORTS_UDP = [53, 123, 5005]
TIMEOUT = 2  # Timeout in seconds for TCP checks
LOG_FILE = 'port_check.log'

# --- Logging Setup ---
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def check_tcp_port(host, port, timeout):
    """Checks if a TCP port is open by attempting to connect."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        if result == 0:
            return True, "Open"
        else:
            return False, f"Closed (Error code: {result})"

def check_udp_port_bind(host, port):
    """
    Checks if a UDP port is available to *bind* to on the local machine.
    Note: Checking if a remote UDP port is 'open' is unreliable without a listener,
    so this checks for local binding ability.
    """
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
            sock.bind((host, port))
        return True, "Available to bind"
    except socket.error as e:
        return False, f"Not available to bind (Error: {e})"

def run_checks_and_log():
    """Runs port checks and writes results to the log file."""
    logging.info(f"--- Starting Port Checks for {HOST} ---")

    print("Checking TCP ports...")
    for port in PORTS_TCP:
        is_open, message = check_tcp_port(HOST, port, TIMEOUT)
        status = "OPEN" if is_open else "CLOSED"
        log_message = f"TCP Port {port}: {status} - {message}"
        print(log_message)
        logging.info(log_message)

    print("\nChecking UDP ports (binding ability)...")
    # For remote UDP checks, consider using netcat as mentioned in search results
    for port in PORTS_UDP:
        is_available, message = check_udp_port_bind(HOST, port)
        status = "AVAILABLE" if is_available else "UNAVAILABLE"
        log_message = f"UDP Port {port}: {status} - {message}"
        print(log_message)
        logging.info(log_message)

    logging.info("--- Port Checks Finished ---")
    print(f"\nResults logged to {os.path.abspath(LOG_FILE)}")

if __name__ == "__main__":
    run_checks_and_log()
