from pydantic import BaseModel


class FileModel(BaseModel):
    id: str
    title: str