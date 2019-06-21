#!/usr/bin/env python3

import _thread
import cfg
import approved
import time
import socket
import re

# specific users
host = cfg.CHAN[1:]
owner = "drcobaltjedi"

# useful chars
adminChar = "&"
userChar = "$"
freebeChar = "*"
todoChar = "!"

# other useful data
todoLength = 1
todo = {}
version = "1.4.3"
currentRelease = "This version adds a todo list for the streamer %s to keep track of things. To add to the list type" \
				 " !addtodo, to see the list type !print, and !delete N to delete the N todo"

CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

# connecting and shit

server = socket.socket()
server.connect((cfg.HOST, cfg.PORT))

server.send(bytes('PASS ' + cfg.PASS + '\r\n', 'utf-8'))
server.send(bytes('NICK ' + cfg.NICK + '\r\n', 'utf-8'))
server.send(bytes('USER ' + cfg.NICK + ' 0 * ' + cfg.NICK + '\r\n', 'utf-8'))
server.send(bytes('JOIN ' + cfg.CHAN + '\r\n', 'utf-8'))




def chat(msg):

	"""
	Send a chat message to the server.
	Keyword arguments:
	sock -- the socket over which to send the message
	msg  -- the message to be sent
	"""

	temp = msg.split("\t")
	for i in temp:
		output = bytes("PRIVMSG {} :{}\r\n".format(cfg.CHAN, i), 'utf-8')
		server.send(output)


# Runs admin commands
# they require special logic for each
def doAdmin(msg):
	MSGPrime = msg.strip("\r\n").strip(adminChar)
	msg = MSGPrime.lower()

	if msg == "off":
		chat("Goodbye")
		exit(0)

	elif "adduser" in msg:
		newName = msg[8:]
		approved.names.append(newName)
		chat("Ye have been added for base commands @" + newName)
		f = open("namesAdd", "a")
		f.write(newName.lower() + "\n")
		f.close()

	elif "addcmd" in msg:
		msg = MSGPrime[7:]
		cmd = msg.split(":")
		approved.commandsDict[cmd[0].lower()] = cmd[1]
		chat("Added new command: " + cmd[0])
		f = open("cmdsAdd", "a")
		f.write('"' + cmd[0].lower() + '": "' + cmd[1] + '",\n')
		f.close()

	elif "addfree" in msg:
		msg = MSGPrime[8:]
		cmd = msg.split(":")
		approved.freeCommands[cmd[0].lower()] = cmd[1]
		chat("Added new freebe: " + cmd[0])
		f = open("freesAdd", "a")
		f.write('"' + cmd[0].lower() + '": "' + cmd[1] + '",\n')
		f.close()


# runs general chat commands
def doThing(msg):
	msg = msg.strip("\r\n").strip(userChar).lower()
	temp = str(approved.commandsDict.get(msg))
	if temp != 'None':
		chat(temp)


# runs freebe commands
def dofreebe(msg):
	a = msg.strip("\r\n").strip(freebeChar).lower()
	temp = str(approved.freeCommands.get(a))

	if temp != "None":
		chat(temp)


# checks is user is an admin
def verifyAdmin(user, msg):
	if user in approved.admins:
		doAdmin(msg)
	else:
		chat("Spitebot does not recognize your authority @" + user)


# checks if user is approved user for basic commands
def verify(user, msg):
	if user in approved.names:
		doThing(msg)

	else:
		chat("Ye are not authorized for base commands @" + user + ". Please ask @DrCobaltJedi for approval.")


def delTODO(msg):
	del todo[msg]


def printTODO():
	for i in todo:
		chat(i + ": " + todo.get(i))
		time.sleep(.1)


def addTODO(msg):
	global todoLength
	todo[todoLength] = msg
	chat("Added todo: " + msg)
	todoLength += 1


def doTODO(msg):
	msgTest = msg.lower()
	if "addtodo" in msgTest:
		addTODO(msg[8:])
	elif "print" in msgTest:
		printTODO()
	elif "delete" in msgTest:
		delTODO(msg[6:].strip())


def main():

	chat("I am Spitebot version " + str(version))
	time.sleep(1.5)
	chat("I am ALIVE")
	time.sleep(1.5)
	chat(currentRelease % host)

	while True:
		response = server.recv(1024).decode("utf-8")

		if response == "PING :tmi.twitch.tv\r\n":
			server.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))

		else:
			username = re.search(r"\w+", response).group(0)  # return the entire match
			message = CHAT_MSG.sub("", response)

			if message[0] == userChar:
				verify(username, message)

			elif message[0] == freebeChar:
				dofreebe(message)

			elif message[0] == adminChar:
				verifyAdmin(username, message)

			elif message[0] == todoChar and (username == host or username == owner):
				doTODO(message[1:])

			elif username == "farmscarecrow":
				chat("Insolent bot")

		time.sleep(1 / cfg.RATE)


if __name__ == '__main__':
	main()
