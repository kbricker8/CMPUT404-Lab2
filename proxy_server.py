import socket
from multiprocessing import Process

BYTES_TO_READ = 4096
PROXY_SERVER_HOST = "127.0.0.1"
PROXY_SERVER_PORT = 8080

def send_request(host, port, request):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host,port))
        client_socket.send(request)
        client_socket.shutdown(socket.SHUT_WR)
        
        data = client_socket.recv(BYTES_TO_READ)
        result = b'' + data
        while len(data) > 0:
            data = client_socket.recv(BYTES_TO_READ)
            result += data
        return result

def handle_connection(conn, addr):
    with conn:
        print(f"Connected by {addr}")

        request = b''
        while True:
            data = conn.recv(BYTES_TO_READ)
            if not data:
                break
            print(data)
            request += data
        response = send_request("www.google.com", 80, request)
        conn.sendall(response)

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((PROXY_SERVER_HOST,PROXY_SERVER_PORT))
        '''
        Allow us to reuse this socket address
        See: https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ
        '''
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.listen(2)
        '''
        Wait for an incomming connection, then create new socket conn
        '''
        conn, addr = server_socket.accept()

        handle_connection(conn, addr)

def start_threaded_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((PROXY_SERVER_HOST,PROXY_SERVER_PORT))
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.listen(2) # Allow queuing of up to 2 connections
        
        while True:
            conn, addr = server_socket.accept()
            thread = Process(target=handle_connection, args=(conn, addr,), daemon=True)
            thread.start()
            thread.join()



#start_server()
start_threaded_server()