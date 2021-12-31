import select
import random
import socket


class Game:
    def __init__(self):
        self.welcome_with_equation = None
        self.name1 = None
        self.name2 = None
        self.client_socket1 = None
        self.client_socket2 = None
        self.first_number = None
        self.second_number = None
        self.time_out = 10.0

    def set_player1(self, team_name, player_socket):
        self.name1 = team_name
        self.client_socket1 = player_socket

    def set_player2(self, team_name, player_socket):
        self.name2 = team_name
        self.client_socket2 = player_socket

    def get_name_by_socket(self,sock):
        if self.client_socket1 == sock:
            return self.name1
        return self.name2

    def get_other_team(self,sock):
        if self.client_socket1 == sock:
            return self.name2
        return self.name1

    def set_player2(self, team_name, player_socket):
        self.name2 = team_name
        self.client_socket2 = player_socket

    def end_game(self):
        self.client_socket1.close()
        self.client_socket2.close()

    def set_equation(self):
        self.first_number = random.randint(0, 9)
        self.second_number = random.randint(0, 9 - self.first_number)
        welcome_message = "Welcome to Quick Maths."
        welcome_message += " Player 1: " + self.name1
        welcome_message += " Player 2: " + self.name2
        welcome_message += "\n=="
        welcome_message += "\nplease answer the following question"
        self.welcome_with_equation = welcome_message + "\n" + str(self.first_number) + " + " + str(
            self.second_number) + " = "

    def send_welcome_with_equation(self):
        self.client_socket1.sendall(self.welcome_with_equation.encode())
        self.client_socket2.sendall(self.welcome_with_equation.encode())

    def start(self):
        self.set_equation()
        print("sending equation.." + "\n" + str(self.first_number) + " + " + str(self.second_number) + " = ")
        try:
            self.send_welcome_with_equation()
        except socket.error as e:
            print("Error while sending welcome message"+str(e))
            return
        # use select to know first one to answer or if there is timeout
        ready_to_get_char, _, _ = select.select([self.client_socket1,self.client_socket2], [], [] , self.time_out)

        try:
            if len(ready_to_get_char) == 0:        # check if it's timeout
                self.client_socket1.sendall(("Time out sorry i hope next year will be better"+"\n").encode())
                self.client_socket2.sendall(("Time out sorry i hope next year will be better"+"\n").encode())
            else:
                c = ready_to_get_char[0].recv(1).decode()
                answer = (self.first_number+self.second_number)
                if c == str(answer):
                    self.client_socket1.sendall(("The Answer Was "+str(answer)+"!\n"+"Congrats to "+self.get_name_by_socket(ready_to_get_char[0])+"\n").encode())
                    self.client_socket2.sendall(("The Answer Was "+str(answer)+"!\n"+"Congrats to "+self.get_name_by_socket(ready_to_get_char[0])+"\n").encode())
                else:
                    self.client_socket1.sendall(("The Answer Was " + str(answer) + "!\n" + "Congrats to "+self.get_other_team(ready_to_get_char[0])+"\n").encode())
                    self.client_socket2.sendall(("The Answer Was " + str(answer) + "!\n" + "Congrats to "+self.get_other_team(ready_to_get_char[0])+"\n").encode())
        except socket.error:
            print("Error while sending results")
        finally:
            self.end_game()





