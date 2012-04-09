import irclib

class IRCConnection(irclib.SimpleIRCClient):
    """
    A simple wrapper for python-irclib.
    """
    def __init__(self, session, server_list, nickname, realname, reconnection_interval=60):
        """Constructor for IRCConnection objects.

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

    def disconnect(self, quit_message):
        """ End the connection. """
        self.connection.disconnect(quit_message)



    ## Various IRC event handlers #############################################

    def on_join(self, c, e):
        """ Called when a user joins a channel we're in. """
        username, channel = self.parse_event(e)
        # We have joined a channel
        if username == self.connection.get_nickname():
            self.session.new_conversation(self, channel)
        # Someone else joined a channel we're in
        else:
            self.session.user_joined_conversation(self, username, channel)

    def on_namereply(self, c, e):
        """ Called to give us a list of users in a channel. """
        args = e.arguments()
        channel = args[1]
        users = args[2].split(" ")
        conversation = self.session.get_conversation(self, channel)
        for u in users:
            conversation.users.append(u)

    def on_part(self, c, e):
        """ Called when a user leaves a channel we're in. """
        username, channel = self.parse_event(e)
        # We have left a channel
        if username == self.connection.get_nickname():
            self.session.leave_conversation(self, channel)
        # Someone else left a channel we're in
        else:
            self.session.user_left_conversation(self, username, channel)

    def on_privmsg(self, c, e):
        """ Called when a channel-specific/private message is received. """
        self._on_message(e)

    def on_pubmsg(self, c, e):
        """ Called when a global/public message is received. """
        self._on_message(e)

    def on_welcome(self, c, e):
        """ Called when the connection is ready. """
        for channel in ["#pyguybot_test"]:
            c.join(channel)



    def parse_event(self, e):
        """ Get the username and channel from an irclib event. """

        # Extract the username from the IRC sender string
        username = irclib.nm_to_n(e.source())
        # See if this is a channel or private message
        if irclib.is_channel(e.target()):
            channel = e.target()
        else:
            channel = None

        return username, channel


    def _on_message(self, e):
        """ The general-purpose message handler. """

        # Parse out the message info
        username, channel = self.parse_event(e)
        message = e.arguments()[0]
        # Pass off the message to the session's callback
        self.session.recv_message(self, username, message, channel)


    def send_message(self, message):
        """ Sends a Message. """

        self.connection.privmsg(message.conversation.name, message.body)


    def __str__(self):
        """ Returns a string repesentation of this IRCConnection. """

        return "<IRCConnection(%s, %s)>" % (id(self), self.server_list[0][0])


    def start(self):
        """ Start the connection. """

        self._connect()
        irclib.SimpleIRCClient.start(self)
