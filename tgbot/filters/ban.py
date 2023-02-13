import typing

from aiogram.dispatcher.filters import BoundFilter

from db_py.db import Database

db = Database()


class BanFilter(BoundFilter):
    key = 'is_banned'

    def __init__(self, is_banned: typing.Optional[bool] = None):
        self.is_banned = is_banned

    async def check(self, obj):
        if self.is_banned is None:
            return False
        user_id = obj.from_user.id
        sql = "SELECT is_ban FROM Users WHERE user_id=?"
        data = db.execute(sql, tuple([user_id]), fetchone=True)
        if not data:
            print("here")
            return False == self.is_banned
        return bool(data[0]) == self.is_banned
