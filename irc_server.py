# Echo server program
import argparse
import logging
import socket
from collections import defaultdict

logging.basicConfig(filename='serverView.log', level=logging.DEBUG)
logger = logging.getLogger()


class IRCServer:

    def __init__(self):
        self.HOST = ''
        self.PORT = None
        self.clients = defaultdict(list)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.channel = '#global'

    # TERMINATE SERVER
    def close(self, msg):
        print(f"\n{msg}")
        print("Server Aborted")
        logger.info(f'SERVER ABORTED')
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
        exit()

    # START SERVER
    def start(self):
        self.s.bind((self.HOST, self.PORT))

    # REGISTER A CLIENT
    def register_client(self, request, connection):

        request = request.split(" ")

        # REGISTER NEW CLIENT CONNECTION
        nickname = request[1]
        username = request[3]
        if nickname not in self.clients:
            self.clients[nickname] = [username, connection]
            # fix later
            commands = "\n==================================\nAVAILABLE COMMANDS:\n" \
                       "NICK - change nickname\n" \
                       "PRIVMSG - send message to channel\n" \
                       "NOTICE - send message to channel\n" \
                       "QUIT - lease server and quit client\n==================================\n\n"

            response1 = commands + '\nConnected and logged in -- ready to go'
            response2 = '\nWelcome ' + nickname + ' to ' + self.channel + '!'
            logger.info(f'{nickname} has been registered on this SERVER')
            connection.sendall(str.encode(response1))
            connection.sendall(str.encode(response2))

        else:
            response = 'ERR_NICKCOLLISION'
            logger.info(f'{response}')
            connection.sendall(str.encode(response))

    # UNREGISTER A CLIENT, CLOSE CONNECTION
    def unregister_client(self, request, connection):
        nickname = self.get_nickname(connection)
        logger.info(f'ATTEMPTING TO UNREGISTER USER {nickname}')
        for nickname, value in self.clients.items():
            if connection == value[1]:
                if len(request.split(" ")) > 1:
                    response = nickname + " has left the chat: " + request.split(':', 1)[1]
                else:
                    response = nickname + " has left the chat"
                logger.info(f'{nickname} has left the SERVER')
                self.broadcast_message(response, connection)
                value[1].shutdown(socket.SHUT_RDWR)
                value[1].close()
                logger.info(f'{nickname} SOCKET CLOSED.')
                self.clients.pop(nickname)
                return

    # ECHO MESSAGE TO CLIENT/S
    def broadcast_message(self, response, connection):
        logger.info(f'SERVER ECHOING MESSAGE TO CHANNEL: {response}')
        connection.sendall(str.encode(response))

    # LISTEN FOR CONNECTION AND CLIENT MESSAGES
    def listen(self, backlog):
        logger.info(f'SERVER LISTENING...')
        self.s.listen(backlog)

        while True:
            conn, addr = self.s.accept()

            with conn:

                print('New Connection by ', addr)
                logger.info(f'New Connection by {addr}')
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    request = data.decode('UTF-8')

                    # REGISTER CLIENT
                    if request.startswith('NICK') and not request.find("USER") == -1:
                        logger.info(f'REGISTERING NEW CLIENT')
                        self.register_client(request, conn)

                    # UNREGISTER CLIENT
                    elif request.startswith('QUIT'):
                        logger.info(f'UNREGISTERING CLIENT')
                        self.unregister_client(request, conn)
                        break

                    # CHANGE NICK
                    elif not request.find("NICK") == -1:
                        logger.info(f'CLIENT CHANGING NICK')
                        self.change_client_nick(request, conn)

                    # ECHO CLIENT MESSAGE
                    elif request.startswith('PRIVMSG') or request.startswith('NOTICE'):

                        if request.startswith('PRIVMSG'):
                            logger.info(f'ECHOING CLIENT PRIVMSG')
                            command = 'PRIVMSG'
                        else:
                            logger.info(f'ECHOING CLIENT NOTICE')
                            command = 'NOTICE'

                        nickname = str()
                        for nick, value in self.clients.items():
                            if conn == value[1]:
                                nickname = nick
                                break

                        msg = request.split(':', 1)[1]
                        request = nickname + " " + command + " " + self.channel + " :" + msg
                        self.broadcast_message(request, conn)

    # VALIDATE PORT NUMBER IN ARGUMENTS
    def validate_port(self, port):
        logger.info("Validating Port...")
        if port is not None:
            if args.port.isnumeric():
                self.PORT = int(args.port)
                logger.info(f'{port} has been validated.')
            else:
                self.close('Invalid PORT number. Server Cannot bind.\n')
                logger.info(f'{port} has been validated.')
        else:
            self.close('No Port Provided. Server Cannot bind.\n')
            logger.info(f'{port} has been validated.')

    # GET NICKNAME BASED ON CONNECTION
    def get_nickname(self, connection):
        if not len(self.clients):
            return " "
        else:
            for nick, value in self.clients.items():
                if connection == value[1]:
                    return nick
            return " "

    # CHANGE NICK - old_nick NICK new_nick OR NICK new_nick
    def change_client_nick(self, request, connection):

        nickname = self.get_nickname(connection)
        logger.info(f"{nickname} is attempting to change their nickname")
        request = request.split(" ")

        if len(request) == 2:

            nickname = request[1]
            if nickname not in self.clients:
                for nick, value in self.clients.items():
                    if connection == value[1]:
                        self.clients[nickname] = self.clients.pop(nick)
                        response = nick + " has changed their nickname to " + nickname
                        logger.info(response)
                        connection.sendall(str.encode(response))

                        break
            else:
                response = 'ERR_NICKNAMEINUSE'
                logger.info(response)
                connection.sendall(str.encode(response))

        else:
            if request[0] in self.clients:
                self.clients[request[2]] = self.clients.pop(request[0])
                response = request[0] + ' changed his nickname to ' + request[2]
                logger.info(response)
                connection.sendall(str.encode(response))

            else:
                response = 'ERR_NICKNAMEINUSE'
                logger.info(response)
                connection.sendall(str.encode(response))


# RECEIVE AND PARSE ARGUMENTS FROM TERMINAL
if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='irc_server')
    parser.add_argument('--port', help='Target port to use.')
    args = parser.parse_args()
    server = IRCServer()
    logger.info(f"Server Object created...")
    print('Server Object Created....')
    server.validate_port(args.port)
    print(f'Server is bound to PORT {server.PORT}\n')
    logger.info(f'Server is bound to PORT {server.PORT}')
    server.start()
    logger.info(f"Server started...")
    print('Server started....\n')

    try:
        print(f'Now listening for clients...\n')
        logger.info(f'Now listening for clients...')
        server.listen(5)

    except:
        server.close("\nERROR!\n")
