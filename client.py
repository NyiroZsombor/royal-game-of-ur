import sys
import queue
import socket
import threading
from consts import *


class Client:

    def init_client(self):
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()

        with open("local_ip.txt") as file:
            host = file.read()

        host = input(f"ip [{host}]: ") or host


        print(f"connecting to {host}...")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((host, PORTS[0]))
            except OSError:
                client.connect((host, PORTS[1]))
            except OSError:
                print("all ports in use")
                sys.exit()
            with open("local_ip.txt", "w") as file:
                file.write(host)

            receive_thread =  threading.Thread(
                target=self.receive,
                daemon=True,
                args=(client,)
            )
            send_thread = threading.Thread(
                target=self.send,
                daemon=True,
                args=(client,)
            )

            send_thread.start()
            receive_thread.start()

            send_thread.join()
            receive_thread.join()
            client.send(b"<exit>")


    def send(self, client):
        while True:
            msg = self.send_queue.get()
            if msg:
                client.send(msg)
                print("<", msg)


    def receive(self, client):
        while True:
            msg = client.recv(1024)
            if msg:
                print(">", msg)
                if len(msg.split()) > 1:
                    for m in msg.split():
                        self.recv_queue.put(m)
                else:
                    self.recv_queue.put(msg)


    def handle_message(self, msg):
        print("#", msg)

        if msg.startswith(b"<move>"):
            if not self.my_turn:
                self.move_sound.play()
            if not self.decode_board(msg):
                print("your turn")
                self.my_turn = True
                self.selected_tile = None
                self.has_rolled = False
                self.move = None

        elif msg.startswith(b"<dark>"):
            self.color = DARK
            self.init()
            print("you are dark")

        elif msg.startswith(b"<light>"):
            self.color = LIGHT
            self.init()
            print("you are light")

        elif msg.startswith(b"<exit>"):
            print("connection closed")
            sys.exit()

        elif msg.startswith(b"<roll>"):
            self.dice = tuple(map(int, msg.strip().split(b"|")[1:]))
            self.roll_sound.play()

        else:
            print("???")


    def decode_board(self, board):
        decoded = list(map(int, board.strip().split(b"|")[1].decode()))

        self.light_pieces = decoded[0]
        self.dark_pieces = decoded[1]
        self.light_score = decoded[2]
        self.dark_score = decoded[3]
        self.board = decoded[4:-1]

        return decoded[-1] == 1


    def encode_board(self):
        return b"".join(map(lambda x: str(x).encode(), (
            self.light_pieces, self.dark_pieces,
            self.light_score, self.dark_score, *self.board
        )))


if __name__ ==  "__main__":
    from app import App
    App().mainloop()
