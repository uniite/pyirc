class RPCService(object):
    def __init__(self, session):
        self.session = session

    def listMethods(cls):
        return ["getConversations", "getMessages", "sendMessage", "getSession"]

    def getConversations(self):
        return self.session.conversations.values()

    def sendMessage(self, conversation_id, message):
        return self.session.send_message(conversation_id, message)

    def getSession(self):
        print self.session.conversations
        return self.session.to_dict()

    def getMessages(self):
        messages = []
        for conv in self.session.conversations.values():
            messages.extend(conv.messages)
        return messages
