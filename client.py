import socket
import helper
import threading
localIP = ""
team_name = "Calculator1\n"
localPort = 13117
bufferSize = 1024
prefix_offer_that_shall_exist = bytes([0xab, 0xcd, 0xdc, 0xba, 0x2])


class InCorrectOfferException(Exception):
    pass


class TcpConnectionException(Exception):
    pass


def decode_udp_offer_and_return_port_number(bytes_array):
    if abs(len(bytes_array)-7) != 0 or bytes_array[0:5] != prefix_offer_that_shall_exist:
        print("Offer is not valid")
        raise InCorrectOfferException()
    return (int(bytes_array[5]) << 8)+int(bytes_array[6])


def connect_over_tcp(address, server_port):
    tcp_socket=None
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("address: ", address,"port: ",server_port, "attempting to connect...")
        tcp_socket.connect((address, server_port))
        print("connected")
        return tcp_socket
    except socket.error:
        if tcp_socket is not None:
            tcp_socket.close()
        raise ConnectionError


def start_game(tcp_socket):
    try:
        # making thread for listening to keyboard
        stop_client_input_event = threading.Event()
        keyboard_thread = threading.Thread(target=listen, args=(tcp_socket, stop_client_input_event,))
        # sending team name
        tcp_socket.sendall(team_name.encode())
        # get welcome message and equation
        welcome_message = tcp_socket.recv(bufferSize).decode()
        print(welcome_message)
        clear_input_buffer()
        keyboard_thread.start()
        data = tcp_socket.recv(bufferSize).decode()
        print(data)
        stop_client_input_event.set()
        tcp_socket.close()
    except socket.error as e:
        print("error occurred in the game: "+str(e))
        return
    finally:
        stop_client_input_event.set()
        tcp_socket.close()


# internet method
def listen(conn_socket, stop_keyboard):
    buffer_listener = helper.KBHit()
    while not stop_keyboard.wait(0):
        if buffer_listener.kbhit():
            char = buffer_listener.getch()
            print(str(char))
            try:
                conn_socket.sendall(str(char).encode())
            except socket.error:
                return


# internet method
def clear_input_buffer():
    while helper.KBHit().kbhit():
        helper.KBHit().getch()


def clear_previous_invitations(client):
    client.settimeout(0.0)
    while True:
        try:
            client.recv(bufferSize)
        except socket.error:
            client.settimeout(None)
            return


def make_udp_server_socker():
    udp_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_server_socket.bind((localIP, localPort))
    return udp_server_socket


def run_client():
    udp_server_socket = make_udp_server_socker()
    message = []
    while True:
        try:
            clear_previous_invitations(udp_server_socket)
            print("Client started, listening for offer requests...")
            message, address = udp_server_socket.recvfrom(bufferSize)
            server_port = decode_udp_offer_and_return_port_number(message)
            tcp_socket = connect_over_tcp(address[0], server_port)
            start_game(tcp_socket)
        except InCorrectOfferException:
            print("Incorrect offer was sent: "+message)
            continue
        except TcpConnectionException:
            print("Connection Fail")
            continue
        except socket.error as e:
            print("Error occurred"+str(e))
            continue


if __name__ == '__main__':
    run_client()
