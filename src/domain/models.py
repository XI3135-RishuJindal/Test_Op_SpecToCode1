# Domain models representing core business logic

class Email:
    def __init__(self, to_address, subject, body):
        self.to_address = to_address
        self.subject = subject
        self.body = body

    # Other business logic methods
