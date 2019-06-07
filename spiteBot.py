import cfg
import approved
import time
import socket
import re

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

	output = bytes("PRIVMSG {} :{}\r\n".format(cfg.CHAN, msg), 'utf-8')
	server.send(output)


# Runs admin commands
# they require special logic for each
def doAdmin(msg):
	msg = msg.strip("\r\n").strip("&").lower()

	if msg == "off":
		chat("Goodbye")
		exit(0)

	elif "adduser" in msg:
		newName = msg[8:]
		approved.names.append(newName)
		chat("You have been added for base commands @" + newName)
		f = open("namesAdd", "a")
		f.write(newName.lower())
		f.close()


# runs general chat commands
def doThing(msg):
	msg = msg.strip("\r\n").strip("$").lower()
	temp = str(approved.commandsDict.get(msg))
	if temp != 'None':
		chat(temp)


# checks is user is an admin
def verifyAdmin(user, msg):
	if user in approved.admins:
		doAdmin(msg)
	else:
		chat("You are not authorized for admin commands @" + user)


# checks if user is approved user for basic commands
# or runs freebe commands
def verify(user, msg):
	a = msg.strip("\r\n").strip("$").lower()
	temp = str(approved.freeCommands.get(a))

	if temp != "None":
		chat(temp)

	elif user in approved.names:
		doThing(msg)

	else:
		chat("You are not authorized for base commands @" + user + ". Please ask @DrCobaltJedi for approval.")


def main():
	chat("I am Spitebot version 1.1")
	time.sleep(3)
	chat("I am ALIVE")

	while True:
		response = server.recv(1024).decode("utf-8")

		if response == "PING :tmi.chat.twitch.tv\r\n":
			server.send("PONG :tmi.chat.twitch.tv\r\n".encode("utf-8"))

		else:
			username = re.search(r"\w+", response).group(0)  # return the entire match
			message = CHAT_MSG.sub("", response)

			if message[0] == '$':
				verify(username, message)

			elif message[0] == '&':
				verifyAdmin(username, message)

			elif username == "farmscarecrow":
				chat("Insolent bot")

		time.sleep(1 / cfg.RATE)


if __name__ == '__main__':
	main()
