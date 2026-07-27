from kiarina.lib.firebase import TokenData, TokenDataCache
from kiarina.utils.file.asyncio import read_json_dict, write_json_dict


class FileTokenCache(TokenDataCache):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    async def get(self) -> TokenData:
        data = await read_json_dict(self.file_path)

        if not data:
            raise FileNotFoundError(f"Token data file not found: {self.file_path}")

        return TokenData.model_validate(data)

    async def set(self, token_data: TokenData) -> None:
        await write_json_dict(
            self.file_path,
            token_data.model_dump(mode="json"),
        )
