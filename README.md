# SIMPLE_CLIENT_AND_SERVER
 COMP445 Lab 2 
 
## DESCRIPTION:
Based on RFC 1459, a client-server chat application is implemented. The client must register a connection with the server before any other commands can be executed. Communication between the client and server is done using the socket library. 
A client registers its connection using the ‘NICK’ command to enter their nickname and the ‘USER’ command to enter a username. A connection is made based on if the server is alive and the nickname provided is unique to the server. Only then can the client automatically join the #global channel and can change their nickname (NICK), send messages to the entire channel (PRIVMSG/NOTICE)  and quit the connection (QUIT). The server validates the messages received and responds. 

Both client and server receive arguments (port and server name) to bind their sockets through the terminal. The server uses a dictionary to store registered clients’ information. The client uses Asynchronous IO to manage the coroutines of the client front end and back end.

## Files:
	banner.txt 
	irc_client.py
	irc_server.py
	patterns.py
	view.py

## Imports:	
[client] argparse, asyncio, logging, patterns, view, time, socket

[server] argparse, logging, socket, defaultdic from collections


## RUNNING PROGRAM INSTRUCTIONS:
 1. Navigate to the directory of the files through command terminal.
 2. Execute the irc_server.py with --server as arguments : python irc_server.py --port <PORT NUMBER>
 3. In another terminal repeat step 1 and Execute the irc_client.py  with --server and port as arguments : python irc_client.py --server <YOUR HOST NAME> --port<PORT NUMBER>
 4. The welcome banner should appear.
 5. In order to connect the client to the server, you must register a connection by entering a nickname and username.
 6. Enter 'NICK' <YOUR NICKNAME>               //nickname must be 9 characters max
 7. Enter 'USER' <YOUR USERNAME>
 8. If nickname is valid and unique, then a successful connection is made with the server.
 9. You can use the following commands:
      
     NICK - change nickname		     => NICK <NEW NICKNAME> 
	
     PRIVMSG - send message to channel  => PRIVMSG #global :<YOUR MESSAGE>
	
     NOTICE - send message to channel => NOTICE #global :<YOUR MESSAGE>
	
     QUIT - lease server and quit client => QUIT   | QUIT : <YOUR REASON>
 
 
GITHUB REPOSITORY:  https://github.com/johansonfelix/SIMPLE_CLIENT_AND_SERVER
 
 
