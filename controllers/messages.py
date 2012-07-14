def send(session, conversation_id, message_body):
    return session.send_message(conversation_id, message_body)
