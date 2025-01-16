from asyncmy import connect
from config import db_data
from typing import Union

class Maria:
    def __init__(self):
        self.host = db_data[0]
        self.user = db_data[1]
        self.password = db_data[2]
        self.db = db_data[3]

    async def start_db(self):
        await self.connector(f"CREATE TABLE IF NOT EXISTS users(user_id BIGINT, account_name TEXT, admin INT, notification_mark INT, notification_auth INT)", commit = True)
        await self.connector(f"CREATE TABLE IF NOT EXISTS accounts(user_id BIGINT, url TEXT, username TEXT, password TEXT, school_id INT)", commit = True)
        await self.connector(f"CREATE TABLE IF NOT EXISTS marks(user_id BIGINT, mark_id BIGINT)", commit=True)

    async def user_exists(self, user_id: int) -> Union[bool, str]:
        account_id = await self.connector(f"SELECT account_name FROM users WHERE user_id = %(user_id)s", {"user_id": user_id})
        if account_id: return account_id[0][0]
        await self.connector(f"INSERT INTO users VALUES(%(user_id)s, 0, 0, 0, 0)", {"user_id": user_id}, True)
        return False

    async def accounts_username_user(self, user_id: int) -> list:
        return (await self.connector(f"SELECT username FROM accounts WHERE user_id = %(user_id)s", {"user_id": user_id}))

    async def add_account(self, user_id: int, url: str, username: str, password: str, school_id: int) -> bool:
        return (await self.connector(f"INSERT INTO accounts VALUES(%(user_id)s, %(url)s, %(username)s, %(password)s, %(school_id)s)", {"user_id": user_id, "url": url, "username": username, "password": password, "school_id": school_id}, True))

    async def select_account(self, user_id: int, account_id: int = "") -> bool:
        return (await self.connector(f"UPDATE users SET account_name = %(account_id)s WHERE user_id = %(user_id)s", {"account_id": account_id, "user_id": user_id}, True))

    async def get_account_user(self, user_id: int) -> list:
        return (await self.connector(f"SELECT url, username, password, school_id FROM accounts WHERE username = (SELECT account_name FROM users WHERE user_id = %(user_id)s)", {"user_id": user_id}))[0]

    async def get_settings(self, user_id: int) -> list:
        return (await self.connector(f"SELECT notification_mark, notification_auth FROM users WHERE user_id = %(user_id)s", {"user_id": user_id}))[0]

    async def update_setting_mark(self, user_id: int, value: int) -> bool:
        return (await self.connector(f"UPDATE users SET notification_mark = %(value)s WHERE user_id = %(user_id)s", {"value": value, "user_id": user_id}, True))

    async def update_setting_auth(self, user_id: int, value: int) -> bool:
        return (await self.connector(f"UPDATE users SET notification_auth = %(value)s WHERE user_id = %(user_id)s", {"value": value, "user_id": user_id}, True))

    async def get_users_notification_mark(self) -> list:
        return (await self.connector(f"SELECT user_id FROM users WHERE notification_mark = 1"))

    async def get_user_marks(self, user_id: int) -> list:
        return (await self.connector(f"SELECT mark_id FROM marks WHERE user_id = %(user_id)s", {"user_id": user_id}))
    
    async def add_user_mark(self, user_id: int, mark_id: int) -> bool:
        return (await self.connector(f"INSERT INTO marks VALUES(%(user_id)s, %(mark_id)s)", {"user_id": user_id, "mark_id": mark_id}, True))

    async def get_users_notification_auth(self) -> list:
        return (await self.connector(f"SELECT user_id FROM users WHERE notification_auth = 1"))

    async def connector(self, sql: str, params: dict = {}, commit: bool = False):
        async with connect(host=self.host, user=self.user, password=self.password, db=self.db, echo=True) as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(sql, params)
                if commit:
                    await connection.commit()
                    return True
                else:
                    return (await cursor.fetchall())