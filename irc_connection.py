import irclib

class IRCConnection(irclib.SimpleIRCClient):
    """A single-server IRC bot class.

    The bot tries to reconnect if it is disconnected.

    The bot keeps track of the channels it has joined, the other
    clients that are present in the channels and which of those that
    have operator or voice modes.  The "database" is kept in the
    self.channels attribute, which is an IRCDict of Channels.
    """
    def __init__(self, session, server_list, nickname, realname, reconnection_interval=60):
        """Constructor for SingleServerIRCBot objects.

        Arguments:

            server_list -- A list of tuples (server, port) that
                           defines which servers the bot should try to
                           connect to.

            nickname -- The bot's nickname.

            realname -- The bot's realname.

            reconnection_interval -- How long the bot should wait
                                     before trying to reconnect.

            dcc_connections -- A list of initiated/accepted DCC
            connections.
        """

        irclib.SimpleIRCClient.__init__(self)

        self.session = session

        self.channels = {}
        self.server_list = server_list
        if not reconnection_interval or reconnection_interval < 0:
            reconnection_interval = 2**31
        self.reconnection_interval = reconnection_interval

        self._nickname = nickname
        self._realname = realname
        for i in ["disconnect"]:
            self.connection.add_global_handler(i,
                                               getattr(self, "_on_" + i),
                                               -10)

    def _connected_checker(self):
        """[Internal]"""
        if not self.connection.is_connected():
            self.connection.execute_delayed(self.reconnection_interval,
                                            self._connected_checker)
            self.jump_server()

    def _connect(self):
        """[Internal]"""
        password = None
        if len(self.server_list[0]) > 2:
            password = self.server_list[0][2]
        try:
            self.connect(self.server_list[0][0],
                         self.server_list[0][1],
                         self._nickname,
                         password,
                         ircname=self._realname)
        except ServerConnectionError:
            pass

    def _on_disconnect(self, c, e):
        """[Internal]"""
        self.channels = {}
        self.connection.execute_delayed(self.reconnection_interval,
                                        self._connected_checker)

    def disconnect(self, msg="I'll be back!"):
        """Disconnect the bot.

        The bot will try to reconnect after a while.

        Arguments:

            msg -- Quit message.
        """
        self.connection.disconnect(msg)
    
    def on_welcome(self, c, e):
        print "Connected!"
        c.join("#pyguybot_test")


    def on_privmsg(self, c, e):
        self._on_message(e)

    def on_pubmsg(self, c, e):
        self._on_message(e)

    def _on_message(self, e):
        username = irclib.nm_to_n(e.source())
        message = e.arguments()[0]
        if irclib.is_channel(e.target()):
            chatroom = e.target()
        else:
            chatroom = None
        self.session.recv_message(self, username, message, chatroom)

    def on_dccmsg(self, c, e):
        self.session.on_message("DCCMSG %s" % " | ".join([e.eventtype(), e.source(), e.target(), str(e.arguments())]))

    def send_message(self, message):
        self.connection.privmsg(message.conversation.name, message.body)

    def __str__(self):
        return "<IRCConnection(%s, %s)>" % (id(self), self.server_list[0][0])


    def start(self):
        """Start the bot."""
        self._connect()
        irclib.SimpleIRCClient.start(self)
