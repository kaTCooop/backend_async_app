from typing import Annotated

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Boolean, Integer, BigInteger
from pydantic import BaseModel, Field, WithJsonSchema


class Base(DeclarativeBase):
	pass


class UserBase(Base):
	__tablename__ = "users"

	user_id: Mapped[int] = mapped_column(primary_key=True)
	email: Mapped[str] = mapped_column(String(50))
	full_name: Mapped[str] = mapped_column(String(100))
	password: Mapped[str] = mapped_column(String(100))
	user_type: Mapped[bool] = mapped_column(Boolean)

	def to_dict(self):
		return {
			'user_id': self.user_id,
			'email': self.email,
			'full_name': self.full_name,
		}


class AccountBase(Base):
	__tablename__ = "accounts"

	account_id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(Integer)
	balance: Mapped[int] = mapped_column(BigInteger)


class TransactionBase(Base):
	__tablename__ = "transactions"

	transaction_id: Mapped[str] = mapped_column(String, primary_key=True)
	account_id: Mapped[int] = mapped_column(Integer)
	user_id: Mapped[int] = mapped_column(Integer)
	amount: Mapped[int] = mapped_column(BigInteger)
	signature: Mapped[str] = mapped_column(String)


class Payment(BaseModel):
	transaction_id: str
	user_id: Annotated[int, Field(le=2147483647, ge=0, strict=True, repr=True, serialization_alias='integer'), WithJsonSchema({'user_id': 'integer', 'examples': [1, 100, 250]})]
	account_id: Annotated[int, Field(le=2147483647, ge=0, strict=True, repr=True, serialization_alias='integer'), WithJsonSchema({'account_id': 'integer', 'examples': [3048, 997]})]
	amount: Annotated[int, Field(le=2147483647, ge=1, strict=True, repr=True, serialization_alias='integer'), WithJsonSchema({'amount': 'integer', 'examples': [1, 200, 1000, 10000]})]
	signature: str = ''


class User(BaseModel):
	user_id: Annotated[int, Field(le=2147483647, ge=0, strict=True, repr=True, serialization_alias='integer'), WithJsonSchema({'user_id': 'integer', 'examples': [3, 100, 250]})]
	email: str
	full_name: str
	password: str
	user_type: bool = Field(examples=[False, True])