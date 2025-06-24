# import time
import socket
from consts import *
from random import randint


def close_conn(clients):
    for c in clients:
        try:
            c.send(b"<exit> ")
        except BrokenPipeError:
            continue
    print(f"connection closed")


def main_loop(clients):
    def except_msg(exp, msg):
        if msg:
            if not msg.startswith(exp):
                print(f"expected {exp.decode()}, got {msg.decode()} instead")
                return True
            return False
        close_conn(clients)
        return True
    
    board = b"77000000000000003033030000000"
    # board = b"77000000000000003033030000020"
    curr_client_idx = randint(0, n_sockets - 1)
    other_client_idx = (curr_client_idx + 1) % n_sockets
    
    curr_client = clients[curr_client_idx]
    other_client = clients[other_client_idx]

    print(f"first player is client {curr_client_idx}")
    
    curr_client.send(b"<light> ")
    other_client.send(b"<dark> ")

    while True:
        try:
            curr_client.send(b"|".join((b"<move>", board + b"0")))
            msg = curr_client.recv(1024).strip()
            if except_msg(b"<roll>", msg): raise BrokenPipeError

            rolls = b"|".join((b"<roll>", *map(
                lambda x: str(x).encode(),
                [randint(0, 1) for _ in range(4)]
            )))

            # time.sleep(2)
            curr_client.send(rolls)
            other_client.send(rolls)

            msg = curr_client.recv(1024).strip().split()
            if except_msg(b"<move>", msg[0]): raise BrokenPipeError
            double_move = msg[0].split(b"|")[1][-1] == ord("1")
            board = msg[0].split(b"|")[1][:-1]

            if not double_move:
                curr_client_idx, other_client_idx = other_client_idx, curr_client_idx
                curr_client, other_client = other_client, curr_client
            else:
                other_client.send(b"|".join((b"<move>", board + b"1")))

        except BrokenPipeError:
            close_conn(clients)
            print(f"by client {curr_client_idx}")
            break


n_sockets = 2

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    try:
        server.bind(("0.0.0.0", PORTS[0]))
        print(f"server is listening on port {PORTS[0]}")

    except OSError:
        server.bind(("0.0.0.0", PORTS[1]))
        print(f"server is listening on port {PORTS[1]}")

    server.listen(n_sockets)
    clients = []

    for i in range(n_sockets):
        client, addr = server.accept()
        clients.append(client)
        print(f"connected by {addr}")

    main_loop(clients)

# server: move(data) -> client
# client: roll -> server
# server: roll -> clients
# client: move(data) -> server
