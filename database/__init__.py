"""
Author Sarthak Vijayvergiya - https://github.com/sarthakvijayvergiya
Description: A Discord bot that helps in launching jobs, setting API keys, and configuring result channels for the Human Protocol.
"""



import aiosqlite


class DatabaseManager:
    def __init__(self, *, connection: aiosqlite.Connection) -> None:
        self.connection = connection

    async def add_api_key(self, user_id: int, api_key: str) -> None:
        """
        This function will add or update the API key and secret for a user in the database.

        :param user_id: The ID of the user.
        :param api_key: The API key secret to store.
        """
        await self.connection.execute(
            "INSERT INTO user_settings(user_id, api_key) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET api_key = excluded.api_key",
            (user_id, api_key),
        )
        await self.connection.commit()
    

    async def add_result_channel(self, user_id: int, channel_id: int) -> None:
        """
        This function will add or update the result channel for a user in the database.

        :param user_id: The ID of the user.
        :param channel_id: The channel ID where results should be published.
        """
        await self.connection.execute(
            "INSERT INTO user_settings(user_id, result_channel_id) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET result_channel_id = excluded.result_channel_id",
            (user_id, channel_id),
        )
        await self.connection.commit()

    async def get_user_settings(self, user_id: int):
        """
        This function retrieves the API key and result channel ID for a user.

        :param user_id: The ID of the user.
        :return: A tuple containing the API key and result channel ID.
        """
        async with self.connection.execute(
            "SELECT api_key, result_channel_id FROM user_settings WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            return await cursor.fetchone()
