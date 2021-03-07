# Echo server program
import argparse
import socket
from collections import defaultdict

HOST = ''  # Symbolic name meaning all available interfaces
PORT = 8080  # Arbitrary non-privileged port


def main(args):
    pass


def close(msg):
    print(msg)
    exit()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='irc_server')
    parser.add_argument('--port', help='Target port to use.')
    args = parser.parse_args()

    print('Server initiated.\n')
    if args.port is not None:
        if args.port.isnumeric():
            PORT = int(args.port)
        else:
            close('Invalid PORT number. Server Cannot bind.\n')
    else:
        close('No Port Provided. Server Cannot bind.\n')

    clients = defaultdict(list)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        print(f'Server is bound to PORT {PORT}\n')
        print(f'Now listening for clients...\n')
        s.listen(5)

        while True:
            conn, addr = s.accept()

            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)

                    if not data:
                        break

                    _request = data.decode('UTF-8')
                    print(_request)

                    if _request.startswith("NICK"):
                        register = _request.split(" ")
                        if len(register) > 2:
                            nickname = register[1]
                            username = register[3]
                            if nickname not in clients:
                                clients[nickname] = [username, conn]
                                # fix later
                                response = 'Welcome ' + nickname + ' to #global'

                                for key in clients.keys():
                                    clients[key][1].sendall(str.encode(response))
                            else:
                                response = 'ERR_NICKCOLLISION'
                                conn.sendall(str.encode(response))

                        elif len(register) == 2:
                            nickname = register[1]
                            if nickname not in clients:
                                for nick, value in clients.items():
                                    if conn == value[1]:
                                        clients[nickname] = clients.pop(nick)
                                        response = nick + " has changed their nickname to " + nickname
                                        for key in clients.keys():
                                            clients[key][1].sendall(str.encode(response))
                                        break
                            else:
                                response = 'ERR_ERRONEUSNICKNAME'
                                conn.sendall(str.encode(response))
                    # FIX NOT RIGHT LOGIC
                    elif _request.split(" ")[1].startswith("NICK"):
                        nick = _request.split(" ")
                        if nick[0] in clients:
                            clients[nick[2]] = clients.pop(nick[0])
                            response = nick[0] + ' changed his nickname to ' + nick[2]

                            for key in clients.keys():
                                clients[key][1].sendall(str.encode(response))

                        else:
                            response = 'ERR_ERRONEUSNICKNAME'
                            conn.sendall(str.encode(response))
