from enum import Enum

from sqlalchemy import BigInteger, Enum as SAEnum, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AddressOption(str, Enum):
    HOME = "до дома"
    PICKUP = "пункт выдачи"


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    ifo: Mapped[str] = mapped_column(String)
    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )
    username: Mapped[str] = mapped_column(String(64))
    address_option: Mapped[AddressOption] = mapped_column(
        SAEnum(AddressOption, name="address_option"), nullable=False
    )
    address: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
