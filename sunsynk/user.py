from typing import Any

from sunsynk.resource import Resource, to_datetime, to_int


class User(Resource):
    """The user account that is logged in."""

    def __init__(self, data: dict[str, Any]):
        self.id = to_int(data.get('id'))
        self.nickname = data.get('nickname')
        self.email = data.get('email')
        self.avatar = data.get('avatar')
        self.mobile = data.get('mobile')
        self.temp_unit = data.get('tempUnit')
        self.company = data.get('company')
        self.user_src = data.get('userSrc')
        self.created_at = to_datetime(data.get('createAt'))
