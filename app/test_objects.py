from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from models import UserBase, AccountBase, TransactionBase
from app_config import admin_password, password_secret_key

from passlib.context import CryptContext
from jose import JWTError, jwt


SECRET_KEY = password_secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def create_user(user: UserBase, session) -> None:
    try:
	    session.add(user)
    except:
        session.rollback()
    else:
        session.commit()


def create_account(account: AccountBase, session) -> None:
    try:
	    session.add(account)
    except:
        session.rollback()
    else:
        session.commit()


def create_default_objects(engine) -> None:
    Session = sessionmaker(engine)

    test_user = UserBase(
        user_id=1,
        email='test@test.ru',
        full_name='Насенков Андрей Николаевич',
        password=get_password_hash('uHaE!DK'),
        user_type=0
    )

    test_admin_user = UserBase(
        user_id=2,
        email='admin@test.ru',
        full_name='Иванов Иван Иванович',
        password=get_password_hash(admin_password),
        user_type=1
    )

    test_account = AccountBase(
        account_id=1,
        user_id=1,
        balance=0
    )

    try:
        create_user(test_user, Session())
    except IntegrityError:
        pass

    try:
        create_user(test_admin_user, Session())
    except IntegrityError:
        pass

    try:
        create_account(test_account, Session())
    except IntegrityError:
        pass