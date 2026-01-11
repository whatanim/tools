import socket
import select
import logging
import time

# Configuration
TCP_PORTS = [5000, 5001]
UDP_PORTS = [5002, 5003]
HOST = '0.0.0.0'  # Listen on all available interfaces
LOG_FILE = 'connection_log.txt'

# Set up logging to a file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE,
                    filemode='a') # 'a' for append mode

def setup_sockets(host, tcp_ports, udp_ports):
    """Creates and binds TCP and UDP sockets."""
    sockets = []
    
    # Setup TCP sockets
    for port in tcp_ports:
        try:
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Reuse address
            tcp_sock.bind((host, port))
            tcp_sock.listen(5) # Listen for up to 5 queued connections
            sockets.append(tcp_sock)
            logging.info(f"TCP server listening on {host}:{port}")
        except Exception as e:
            logging.error(f"Failed to set up TCP port {port}: {e}")

    # Setup UDP sockets
    for port in udp_ports:
        try:
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.bind((host, port))
            sockets.append(udp_sock)
            logging.info(f"UDP server listening on {host}:{port}")
        except Exception as e:
            logging.error(f"Failed to set up UDP port {port}: {e}")
            
    return sockets

def handle_tcp_connection(sock):
    """Handles a new TCP connection."""
    try:
        conn, addr = sock.accept()
        logging.info(f"New TCP connection from: {addr[0]}:{addr[1]} on port {sock.getsockname()[1]}")
        # In a real application, you would handle data exchange here, possibly in a new thread.
        # For this example, we just log the connection and close it after a brief interaction.
        conn.sendall(b"Hello from the TCP server!\n")
        conn.close()
    except Exception as e:
        logging.error(f"Error handling TCP connection: {e}")

def handle_udp_packet(sock):
    """Handles a new UDP packet."""
    try:
        data, addr = sock.recvfrom(1024) # Buffer size is 1024 bytes
        logging.info(f"Received UDP packet from: {addr[0]}:{addr[1]} on port {sock.getsockname()[1]}. Data: {data.decode().strip()}")
        # You can send a response back to the client if needed
        # sock.sendto(b"ACK\n", addr)
    except Exception as e:
        logging.error(f"Error handling UDP packet: {e}")

def main():
    listening_sockets = setup_sockets(HOST, TCP_PORTS, UDP_PORTS)
    if not listening_sockets:
        print("No sockets are listening. Exiting.")
        return

    print(f"Server running, logging connections to {LOG_FILE}. Press Ctrl+C to stop.")
    
    try:
        while True:
            # Use select to wait for I/O readiness on any of the sockets
            readable, _, _ = select.select(listening_sockets, [], [])
            
            for sock in readable:
                if sock.type == socket.SOCK_STREAM:
                    handle_tcp_connection(sock)
                elif sock.type == socket.SOCK_DGRAM:
                    handle_udp_packet(sock)
                else:
                    logging.warning("Unknown socket type received")
    except KeyboardInterrupt:
        print("Server is shutting down.")
    finally:
        for sock in listening_sockets:
            sock.close()
        logging.info("Server stopped and sockets closed.")

if __name__ == "__main__":
    main()
