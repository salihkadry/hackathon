import socket
import time
from game import Game

BUFF_SIZE = 1024
offer_message = bytes([0xab, 0xcd, 0xdc, 0xba, 0x2,0x27,0x76])
tcp_port = 10102
udp_port = 13117


def create_broadcast_udp_socket():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return udp_socket


def create_tcp_listening_socket():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", tcp_port))
    server_socket.listen()
    server_socket.settimeout(10)
    return server_socket


def start_server():
    while True:
        game = Game()
        get_clients_for_the_game(game)
        print("sleep for 10 seconds...")
        time.sleep(10)
        print("start game...")
        game.start()


def get_clients_for_the_game(game):
    broadcast_socket = create_broadcast_udp_socket()
    server_socket = create_tcp_listening_socket()
    while True:
        broadcast_socket.sendto(offer_message, ('<broadcast>', udp_port))
        client_socket = None
        try:
            client_socket, address = server_socket.accept()
            client_socket.settimeout(10)
            print(address)
            team_name = client_socket.recv(BUFF_SIZE).decode()
            if game.name1 is None:
                print("Team1: ", team_name, "have been connected")
                game.set_player1(team_name, client_socket)
            elif game.name2 is None:
                print("Team2: ", team_name, "have been connected")
                game.set_player2(team_name, client_socket)
                return
        except socket.timeout:
            pass
        except socket.error as e:
            if client_socket is not None:
                client_socket.close()
            print("Error while getting the team name: "+e.__str__()+"\nstart searching for teams again")


if __name__ == '__main__':
    start_server()
