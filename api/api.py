class BasicApi:

    # noinspection PyMethodMayBeStatic
    def get_body(self, body_code, body_type, body_msg, body_content, body_extra=None):
        if body_extra is None:
            body_extra = {}
        body = {
                   'code': body_code,
                   'type': body_type,
                   'msg': body_msg,
                   'content': body_content
               }
        for k in body_extra:
            body[k] = body_extra[k]
        return body, body_code
