from pydantic import BaseModel, Field


class AccountInput(BaseModel):
    alias: str
    email: str
    password: str


class ScrapeRequest(BaseModel):
    accounts: list[AccountInput]
    keyword: str
    region: str
    max_results: int = Field(default=10, ge=1, le=500)
    max_seconds: int = Field(default=300, ge=10, le=3600)
    workers: int = Field(default=1, ge=1, le=5)