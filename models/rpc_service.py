class RPCService(object):
    @classmethod
    def listMethods(cls):
        return ["getConversations", "getMessages", "sendMessage", "getSession"]

    @classmethod
    def getConversations(cls):
        return session.conversations.values()

    @classmethod
    def sendMessage(cls, conversation_id, message):
        return session.send_message(conversation_id, message)

    @classmethod
    def getSession(cls):
        return session.to_dict()

    @classmethod
    def getMessages(cls):
        messages = []
        for conv in session.conversations.values():
            messages.extend(conv.messages)
        return messages
