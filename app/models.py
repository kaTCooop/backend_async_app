from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Boolean, Integer, BigInteger


class Base(DeclarativeBase):
	pass


class UserBase(Base):
	__tablename__ = "users"

	user_id: Mapped[int] = mapped_column(primary_key=True)
	email: Mapped[str] = mapped_column(String(50))
	full_name: Mapped[str] = mapped_column(String(100))
	password: Mapped[str] = mapped_column(String(30))
	user_type: Mapped[bool] = mapped_column(Boolean)


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