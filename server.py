# import time
import sys
import socket
from consts import *
from random import randint

class Server:

    @staticmethod
    def bind_server(server):
        for i in range(50):
            port = PORTS[0] + i // 2
            try:
                server.bind(("0.0.0.0", port))
            except OSError:
                try:
                    port = PORTS[1] + i // 2
                    server.bind(("0.0.0.0", port))
                except OSError:
                    continue
            return port
        else:
            print("all ports are in use")


    def __init__(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as soc:
            soc.connect(("10.255.255.255", 1))

            self.ip = soc.getsockname()[0]


    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            port = self.bind_server(server)

            print(f"server is listening on ip {self.ip}:{port}")
            if "--debug" in sys.argv:
                print("[!] server is running in debug mode")

            server.listen(2)
            clients = []

            for _ in range(2):
                client, addr = server.accept()
                clients.append(client)
                print(f"connected by {addr}")

            self.main_loop(clients)


    def close_conn(self, clients):
        for c in clients:
            try:
                c.send(b"<exit> ")
            except BrokenPipeError:
                continue
        print(f"connection closed")

    
    def except_msg(self, exp, msg):
        if msg:
            if not msg.startswith(exp):
                print(f"expected {exp.decode()}, got {msg.decode()} instead")
                raise ValueError
            return False
        raise BrokenPipeError


    def main_loop(self, clients):
        if "--debug" in sys.argv:
            board = (b"0066"
            b"000"
            b"000"
            b"000"
            b"000"
            b"303"
            b"303"
            b"112"
            b"112"
            b"0")
            # board = b"77000000000000003033030000000"
        else:
            board = b"77000000000000003033030000000"
        
        curr_client_idx = randint(0, 1)
        
        curr_client = clients[curr_client_idx]
        other_client = clients[curr_client_idx ^ 1]

        print(f"first player is client {curr_client_idx}")
        
        curr_client.sendall(b"<light> ")
        other_client.sendall(b"<dark> ")

        while True:
            try:
                curr_client.sendall(b"|".join((b"<move>", board + b"0")))
                msg = curr_client.recv(1024).strip()
                self.except_msg(b"<roll>", msg)

                rolls = b"|".join((b"<roll>", *map(
                    lambda x: str(x).encode(),
                    [randint(0, 1) for _ in range(4)]
                )))

                # time.sleep(2)
                curr_client.sendall(rolls)
                other_client.sendall(rolls)

                msg = curr_client.recv(1024).strip()
                self.except_msg(b"<move>", msg)
                msg = msg.split()[0]                    # in case of multiple msgs, select 1st
                payload = msg.split(b"|")[1]            # get payload
                double_move = payload[-1] == ord("1")   # indexing byte returns int
                board = payload[:-1]

                if not double_move:
                    curr_client_idx ^= 1
                    curr_client = clients[curr_client_idx]
                    other_client = clients[curr_client_idx ^ 1]
                else:
                    other_client.sendall(b"|".join((b"<move>", board + b"1")))

            except BrokenPipeError:
                self.close_conn(clients)
                print(f"by client {curr_client_idx}")
                break


if __name__ == "__main__":
    Server().start_server()

