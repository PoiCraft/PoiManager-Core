import random
from datetime import datetime

token_char = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class TokenManager:
    token_list = {}

    class Token:
        def __init__(self):
            self.created_at = datetime.now()
            self.removed_at = self.created_at.replace(day=self.created_at.day + 1)
            self.token = random.sample(token_char, 32)

    def getToken(self):
        token = self.Token()
        self.token_list[token.token] = token
        return token
