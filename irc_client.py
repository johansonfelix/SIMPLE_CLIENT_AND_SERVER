#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021
#
# Distributed under terms of the MIT license.

"""
Description:

"""
import argparse
import asyncio
import logging
import threading
from random import random

import patterns
import view
import time
import socket

logging.basicConfig(filename='view.log', level=logging.DEBUG)
logger = logging.getLogger()

result_available = threading.Event()


class IRCClient(patterns.Subscriber):

    def __init__(self):
        super().__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.nickname = None
        self._run = True
        self.HOST = str()
        self.PORT = 0

    def set_view(self, view):
        self.view = view

    def update(self, msg):
        # Will need to modify this
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        logger.info(f"IRCClient.update -> msg: {msg}")
        self.process_input(msg)

    def process_input(self, msg):
        # Will need to modify this

        if msg == 'QUIT':
            self.view.put_msg("\n" + msg)
            # Command that leads to the closure of the process
            raise KeyboardInterrupt

        elif msg.startswith('NICK'):
            self.view.put_msg("\n" + msg)
            #make sure length of nickname is max 9 chars!
            response = self.send_request(msg)
            self.view.put_msg(f'\n{response}')

        elif msg.startswith('PRIVMSG'):
            self.view.put_msg("\n" + msg)
            # make sure length of nickname is max 9 chars!
            response = self.send_request(msg)
            self.view.put_msg(f'\n{response}')

        elif msg.startswith('NOTICE'):
            self.view.put_msg("\n" + msg)
            # make sure length of nickname is max 9 chars!
            response = self.send_request(msg)
            self.view.put_msg(f'\n{response}')


        else:
            # CHANGEpy
            self.view.put_msg('\nInvalid Command\n')

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    def send_request(self, msg):
        self.s.sendall(str.encode(msg))
        data = self.s.recv(1024).decode('UTF-8')
        return data

    def verify_host_port(self, host, port):

        if host is not None and port is not None:
            return port.isnumeric() and not host.isnumeric()

    def input_nick_user(self):
        done = False

        while not done:
            _str = self.view.get_input()
            self.view.put_msg(f"\n{_str.decode('UTF-8')}")
            _str = _str.decode('UTF-8').split(" ")
            if _str[0] == 'NICK' and _str[1] is not None:
                if len(_str[1]) <= 9:
                    self.nickname = _str[1]
                    if self.username is not None:
                        done = True

            elif _str[0] == 'USER' and _str[1] is not None:
                self.username = _str[1]
                if self.nickname is not None:
                    done = True

            else:
                if not done:
                    self.view.put_msg("\nPlease enter valid username and nickname to connect using commands NICK and "
                                      "USER.")

    async def run(self):

        """
        Driver of your IRC Client
        """
        # Check valid HOST and PORT, make port an int
        if self.verify_host_port(host=self.HOST, port=self.PORT):
            self.PORT = int(self.PORT)
        else:
            self.view.put_msg(f"Invalid arguments.\n")
            raise KeyboardInterrupt

        # Wait for Client nickname and username

        self.input_nick_user()

        # self.connect_to_server() REGISTER TO SERVER, CHECK USERNAME/NICKNAME EXITS, ETC.

        self.s.connect((self.HOST, self.PORT))
        _str = 'NICK ' + self.nickname + " USER " + self.username
        self.s.sendall(str.encode(_str))
        data = self.s.recv(1024).decode('UTF-8')
        if data.startswith("Welcome"):
            self.view.put_msg(f"\n{data}")
        else:
            self.view.put_msg(f"\n{data}")
            self.close()








        # self.view.put_msg("\nSuccess!")
        # exit()
        # # Once client nickname and username received, setup connection with server
        # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        #     s.connect((self.HOST, self.PORT))
        #     s.sendall(b'Hello, world')
        #     data = s.recv(1024)

        # Loop receving input from client. If client

        # Remove this section in your code, simply for illustration purposes
        # for x in range(10):
        #     self.add_msg(f"call after View.loop: {x}")
        #     await asyncio.sleep(2)

    def close(self):
        # Terminate connection
        logger.debug(f"Closing IRC Client object")
        self.view.put_msg(f"\nClosing IRC Client object")
        time.sleep(2.5)

    # MAKE SURE NICKNAME IS 8 CHARACTERS LONG
    def input_nick(self):
        self.view.put_msg("\nNickname: ")
        nickname = self.view.get_input().decode('UTF-8')
        self.view.put_msg(nickname)

        while not len(nickname):
            self.view.put_msg("\nNickname: ")
            nickname = self.view.get_input().decode('UTF-8')
            self.view.put_msg(nickname)
        return nickname

    def input_username(self):
        self.view.put_msg("\nUsername: ")
        username = self.view.get_input().decode('UTF-8')
        self.view.put_msg(username)

        while not len(username):
            self.view.put_msg("\nUsername: ")
            username = self.view.get_input().decode('UTF-8')
            self.view.put_msg(username)
        return username


def main(args):
    # Pass your arguments where necessary to client
    client = IRCClient()
    client.HOST = args.server
    client.PORT = args.port

    logger.info(f"Client object created")
    with view.View() as v:
        logger.info(f"Entered the context of a View object")
        client.set_view(v)
        logger.debug(f"Passed View object to IRC Client")
        v.add_subscriber(client)
        logger.debug(f"IRC Client is subscribed to the View (to receive user input)")

        # v.put_msg("Enter Nickname: ")
        # nickname = v.get_input().decode('utf-8')
        # v.put_msg(f'{nickname}\n')
        async def inner_run():
            await asyncio.gather(
                v.run(),
                client.run(),
                return_exceptions=True,
            )

        try:
            asyncio.run(inner_run())
        except KeyboardInterrupt as e:
            logger.debug(f"Signifies end of process")
    client.close()


if __name__ == "__main__":
    # Parse your command line arguments here
    parser = argparse.ArgumentParser(prog='irc_client')
    parser.add_argument('--server', help='Target server to initiate a connection to.')
    parser.add_argument('--port', help='Target port to use.')
    args = parser.parse_args()
    main(args)
