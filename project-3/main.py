import socket
import concurrent.futures


def pscan(port, target):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        s = sock.connect_ex((target, port))
        if s == 0:
            return True
        else:
            return False


def loop(target):
    """
    This function performs a multithreaded port scan on the specified target IP address.
    It uses a ThreadPoolExecutor to manage concurrent threads that check each port from 1 to 1024.
    The results are collected and printed as they become available, allowing for efficient scanning of multiple ports simultaneously.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(pscan, port, target): port for port in range(1, 1025)}
        for future in concurrent.futures.as_completed(futures):
            port = futures[future]
            is_open = future.result()
            if is_open:
                print(f'Port {port} is open on {target}.')

    
if __name__ == '__main__':
    target_ip = input('Enter target IP address (default is local machine): ')
    if target_ip:
        loop(target_ip)
    else:
        loop(socket.gethostbyname(socket.gethostname()))