from pydantic import BaseModel, Field


class TextFilePurgeSchema(BaseModel):
    """
    Purge text files from the current History by FileInfo ID.

    This removes the full text FileInfo values stored in History. It does not delete
    underlying asset or cache data. IDs that are missing or belong to non-text files
    are reported without preventing other requested text files from being purged.
    """

    ids: list[str] = Field(
        min_length=1,
        description="One or more FileInfo IDs to purge from the current History.",
    )
