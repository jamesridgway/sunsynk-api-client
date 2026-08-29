import datetime
from typing import Any

from sunsynk.resource import Resource, to_int


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
        created_at = data.get('createAt')
        self.created_at = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ") if created_at else None
