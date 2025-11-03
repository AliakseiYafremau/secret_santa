from __future__ import annotations

from dataclasses import dataclass
from os import environ


def get_env_variable(key: str) -> str:
    value = environ.get(key)
    if value is None:
        raise ValueError(f"Write {key} in the environment variables.")
    return value


def load_config() -> Config:
    return Config(
        bot_token_1=get_env_variable("BOT_TOKEN_1"),
        bot_token_2=get_env_variable("BOT_TOKEN_2"),
        admin_id=get_env_variable("ADMIN_ID"),
    )


@dataclass
class Config:
    bot_token_1: str
    bot_token_2: str
    admin_id: str
