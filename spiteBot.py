import cfg
import approved
import time
import socket
import re

CHAT_MSG = re.compile(r"^:\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")

# network functions go here

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


def doAdmin(msg):
	msg = msg.strip("\r\n").strip("&")

	if msg.lower() == "off":
		chat("Goodbye")
		exit(0)

	elif "adduser" in msg.lower():
		newName = msg[8:]
		approved.names.append(newName)
		chat("You have been added for base commands @" + newName)
		f = open("namesAdd", "a")
		f.write(newName.lower())
		f.close()


def doThing(msg):
	msg = msg.strip("\r\n").strip("$")
	temp = str(approved.commandsDict.get(msg.lower()))
	if temp != 'None':
		chat(temp)


def verifyAdmin(user, msg):
	if user in approved.admins:
		doAdmin(msg)
	else:
		chat("You are not authorized for admin commands @" + user)


def verify(user, msg):
	if user in approved.names:
		doThing(msg)
	else:
		chat("You are not authorized for base commands @" + user + ". Please ask @DrCobaltJedi for approval.")


def main():
	chat("I am Spitebot")
	time.sleep(3)
	chat("I am ALIVE")
	while True:
		response = server.recv(1024).decode("utf-8")
		if response == "PING :tmi.twitch.tv\r\n":
			server.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
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
