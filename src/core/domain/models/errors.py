class EmailAlreadyInUseError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email {email} is already in use")