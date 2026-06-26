class UserRepository:
    def __init__(self, persistence_layer):
        self.persistence_layer = persistence_layer

    def add_user(self, user):
        self.persistence_layer.save(user)
