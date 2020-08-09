class BasicApi:

    """Basic Api

    It has a function that can build a formatted JSON as body.
    """

    # noinspection PyMethodMayBeStatic
    def get_body(self, body_code, body_type, body_msg, body_content, body_extra=None):
        """A function to build a formatted JSON as body.

        This function will build a body kile {
                   'code': body_code,
                   'type': body_type,
                   'msg': body_msg,
                   'content': body_content
               }

        :param body_code: The code of the body, such as 200, 404 and 403.
        :type body_code int
        :param body_type: The type of the body, such as 'bds_in'.
        :type body_type str
        :param body_msg: The message of the body, such as 'OK'.
        :type body_msg: str
        :param body_content: The content of the body.
        :param body_extra: The extra part of the body, require a dict like {'key1':'value1','key2':'value2'}.
        :type body_extra: dict
        :return: Just return this function's return, flask will do the rest.
        """
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
