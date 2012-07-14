def join(session, name):
    return session.join_conversation(name)

def leave(session, name):
    return session.leave_conversation(name)

def set_current(session, conversation_id):
    session.current_conversation_id = int(conversation_id)
    print "Set current Conversation to %s" % conversation_id
    return True
