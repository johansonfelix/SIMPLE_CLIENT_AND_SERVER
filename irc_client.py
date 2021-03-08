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
import patterns
import view
import time
import socket

logging.basicConfig(filename='clientView.log', level=logging.DEBUG)
logger = logging.getLogger()


class IRCClient(patterns.Subscriber):

    def __init__(self):
        super().__init__()
        self.view = None
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = None
        self.nickname = None
        self._run = True
        self.HOST = str()
        self.PORT = 0

    def set_view(self, v):
        self.view = v

    def update(self, msg):
        if not isinstance(msg, str):
            raise TypeError(f"Update argument needs to be a string")
        elif not len(msg):
            # Empty string
            return
        logger.info(f"IRCClient.update -> msg: {msg}")
        self.process_input(msg)

    def process_input(self, msg):

        if self.username is None or self.nickname is None:
            self.view.put_msg("\nCannot Register Connection. No nickname and/or username provided. Try again "
                              "later.\nExiting...")
            raise KeyboardInterrupt

        # QUIT COMMAND
        if msg.startswith('QUIT'):
            # self.view.put_msg("\n" + msg)
            self.send_request(msg)
            self.receive()
            raise KeyboardInterrupt

        # NICK COMMAND
        elif msg.startswith('NICK'):
            # self.view.put_msg("\n" + msg)

            if 0 < (len(msg.split(" ")[1])) <= 9:
                self.send_request(msg)
                self.receive()
            else:
                return

        # PRIVMSG AND NOTICE COMMAND
        elif msg.split(" ")[0] == 'PRIVMSG' or msg.split(" ")[0] == 'NOTICE':

            if msg.split(" ")[1] is None:
                return
            else:
                self.send_request(msg)
                self.receive()
        else:
            self.view.put_msg(f'\n{msg} - INVALID COMMAND')

    def add_msg(self, msg):
        self.view.add_msg(self.username, msg)

    # SEND DATA TO SERVER
    def send_request(self, msg):
        self.s.sendall(str.encode(msg))

    # READER FOR NICK AND USER
    def input_nick_user(self):
        done = False

        while not done:
            _str = self.view.get_input()
            self.view.put_msg(f"\n{_str.decode('UTF-8')}")
            _str = _str.decode('UTF-8').split(" ")
            if _str[0] == 'NICK' and 0 < len(_str[1]) <= 9:
                self.nickname = _str[1]
                if self.username is not None:
                    done = True

            elif _str[0] == 'USER' and _str[1] is not None:
                self.username = _str[1]
                if self.nickname is not None:
                    done = True

            else:
                if not done:
                    if self.nickname is None and self.username is None:
                        self.view.put_msg(
                            "\nPlease enter valid nickname and username to connect using commands NICK and USER")
                    elif self.nickname is None:
                        self.view.put_msg("\nPlease enter valid nickname to connect using NICK command")
                    elif self.username is None:
                        self.view.put_msg("\nPlease enter valid username to connect using USER command")

    # client driver
    async def run(self):

        """
        Driver of IRC Client
        """

        # Check valid HOST and PORT, make port an int
        if verify_host_port(host=self.HOST, port=self.PORT):
            self.PORT = int(self.PORT)
        else:
            self.view.put_msg(f"Invalid arguments.\n")
            raise KeyboardInterrupt

        # Wait for user to enter Client nickname and username
        self.input_nick_user()

        # REGISTER CLIENT TO SERVER, IF NICK already exists then CONNECTION CLOSES
        try:
            self.s.settimeout(3)
            self.s.connect((self.HOST, self.PORT))
        except socket.error:
            self.view.put_msg("\nERR_NOSUCHSERVER ")
            raise KeyboardInterrupt

        _str = 'NICK ' + self.nickname + " USER " + self.username
        self.s.sendall(str.encode(_str))
        self.receive()

    # TERMINATE CLIENT
    def close(self):

        logger.debug(f"Closing IRC Client object")
        self.view.put_msg(f"\nClosing IRC Client object")
        time.sleep(2.5)

    # receive data from server
    def receive(self):
        self.s.settimeout(1)
        try:
            while True:
                data = self.s.recv(1024).decode('UTF-8')
                if not data:
                    break
                self.view.put_msg(f"\n{data}")
        except socket.timeout:
            pass


# MAIN METHOD - pass arguments and sync view with backend client
def main(arguments):
    client = IRCClient()
    client.HOST = arguments.server
    client.PORT = arguments.port

    logger.info(f"Client object created")
    with view.View() as v:
        logger.info(f"Entered the context of a View object")
        client.set_view(v)
        logger.debug(f"Passed View object to IRC Client")
        v.add_subscriber(client)
        logger.debug(f"IRC Client is subscribed to the View (to receive user input)")

        async def inner_run():
            await asyncio.gather(
                v.run(),
                client.run(),
                return_exceptions=True,
            )

        try:
            asyncio.run(inner_run())
        except KeyboardInterrupt:
            logger.debug(f"Signifies end of process")
    client.close()


# verify port number is a number
def verify_host_port(host, port):
    if host is not None and port is not None:
        return port.isnumeric() and not host.isnumeric()


# receive arguments from terminal
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='irc_client')
    parser.add_argument('--server', help='Target server to initiate a connection to.')
    parser.add_argument('--port', help='Target port to use.')
    args = parser.parse_args()
    main(args)
