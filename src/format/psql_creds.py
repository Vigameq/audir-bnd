

class PsqlCreds:
    def __init__(self, user_name, password, host, database, port, sslmode):
        self.user_name = user_name
        self.password = password
        self.host = host
        self.database = database
        self.port = port
        self.sslmode = sslmode