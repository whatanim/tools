import socket
import threading
import logging
import sys

# Configure logging to write to a file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='connections.log',
                    filemode='a') # Append mode

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

HOST = '0.0.0.0'  # Listen on all available interfaces
TCP_PORT = 65432  # Non-privileged port for TCP
UDP_PORT = 65433  # Non-privileged port for UDP

def handle_tcp_client(conn, addr):
    """Handle a single TCP client connection."""
    logging.info(f"TCP connection established from {addr}")
    try:
        with conn:
            # You can add logic here to handle data exchange
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # Optional: log received data
                # logging.info(f"Received data from {addr[0]}:{addr[1]}: {data.decode()}")
                conn.sendall(data) # Echo data back
    except Exception as e:
        logging.error(f"Error with TCP connection from {addr}: {e}")
    finally:
        logging.info(f"TCP connection closed with {addr}")

def start_tcp_server():
    """Starts the TCP server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, TCP_PORT))
            s.listen()
            logging.info(f"TCP server listening on {HOST}:{TCP_PORT}")
            while True:
                conn, addr = s.accept()
                # Start a new thread to handle the client connection
                client_thread = threading.Thread(target=handle_tcp_client, args=(conn, addr))
                client_thread.start()
        except Exception as e:
            logging.error(f"Failed to start TCP server: {e}")
            sys.exit(1)

def start_udp_server():
    """Starts the UDP server."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.bind((HOST, UDP_PORT))
            logging.info(f"UDP server listening on {HOST}:{UDP_PORT}")
            while True:
                # recvfrom returns data and the client's address
                data, addr = s.recvfrom(1024)
                # For UDP, the 'connection' is connectionless, but we log the sender's address
                logging.info(f"Received UDP packet from {addr}")
                # Optional: log received data
                # logging.info(f"Received data via UDP from {addr[0]}:{addr[1]}: {data.decode()}")
                s.sendto(data, addr) # Echo data back
        except Exception as e:
            logging.error(f"Failed to start UDP server: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Run both servers concurrently in separate threads
    tcp_thread = threading.Thread(target=start_tcp_server)
    udp_thread = threading.Thread(target=start_udp_server)

    tcp_thread.start()
    udp_thread.start()

    tcp_thread.join()
    udp_thread.join()
