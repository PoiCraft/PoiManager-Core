from flask import Flask

from auth.Token import TokenManager
from database import BdsLogger


class BasicApi:

    # noinspection PyMethodMayBeStatic
    def get_body(self, body_code, body_type, body_msg):
        return {
                   'code': body_code,
                   'type': body_type,
                   'msg': body_msg
               }, body_code
