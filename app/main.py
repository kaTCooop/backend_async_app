from functools import wraps
from hashlib import sha256
from typing import Union

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from core import app, conn, meta
from app_config import admin_password, admin_cookie, payment_secret_key
from auth.dependencies import get_current_user, get_db, get_current_admin
from auth.routes import router as auth_router
from models import UserBase, Payment, User
from test_objects import get_password_hash


allow_empty_signature = False


app.include_router(auth_router, prefix='/auth', tags=['auth'])
users = meta.tables['users']
accounts = meta.tables['accounts']
transactions = meta.tables['transactions']


def do_and_commit(query):
    try:
        conn.execute(query)
    except:
        conn.rollback()
        raise HTTPException(status_code=502, detail="Database error")
    else:
        conn.commit()


@app.get("/", tags=['user_actions'])
def get_info(user: UserBase = Depends(get_current_user)) -> dict:
    user = user.to_dict()
    return {'user_id': user['user_id'], 'email': user['email'], 'full_name': user['full_name']}


@app.get("/accounts", tags=['user_actions'])
def get_accounts(user: UserBase = Depends(get_current_user)) -> list[dict]:
    accounts = meta.tables['accounts']
    query = select(accounts).where(accounts.c.user_id == user.user_id).order_by(accounts.c.account_id)
    accounts_output = conn.execute(query).mappings().all()
    return accounts_output


@app.get("/transactions", tags=['user_actions'])
def get_transactions(user: UserBase = Depends(get_current_user)) -> list[dict]:
    transactions = meta.tables['transactions']
    query = select(transactions).where(transactions.c.user_id == user.user_id)
    transactions_output = conn.execute(query).mappings().all()
    return transactions_output


@app.get("/admin", tags=['admin_actions'])
def get_admin_info(admin: UserBase = Depends(get_current_admin)) -> dict:
    admin = admin.to_dict()
    return {'user_id': admin['user_id'], 'email': admin['email'], 'full_name': admin['full_name']}


@app.get('/list', tags=['admin_actions'])
def list_users(admin: UserBase = Depends(get_current_admin)) -> list[dict]:
        query = select(users).order_by(users.c.user_id)
        users_output = conn.execute(query).mappings().all()
        return users_output

@app.post('/add_user', tags=['admin_actions'])
def add_user(user: User, admin: UserBase = Depends(get_current_admin)):
    query = select(users).where(users.c.user_id == user.user_id)
    result = conn.execute(query).mappings().all()

    if not result:
        query = users.insert().values(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            password=get_password_hash(user.password),
            user_type=user.user_type
        )
    else:
        query = users.update().where(users.c.user_id == user_id).values(
            email=user.email,
            full_name=user.full_name,
            password=get_password_hash(user.password),
            user_type=user.user_type
        )
    
    do_and_commit(query)


@app.post('/delete', tags=['admin_actions'])
def delete_user(user_id: int, admin: UserBase = Depends(get_current_admin)):
    query = select(users).where(users.c.user_id == user_id)
    result = conn.execute(query).mappings().all()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    query = users.delete().where(users.c.user_id == user_id)
    do_and_commit(query)

    query = accounts.delete().where(accounts.c.user_id == user_id)
    do_and_commit(query)

    query = transactions.delete().where(transactions.c.user_id == user_id)
    do_and_commit(query)


@app.post('/inspect_accounts', tags=['admin_actions'])
def get_accounts_of_user(user_id: int, admin: UserBase = Depends(get_current_admin)) -> list[dict]:
    query = select(accounts).where(accounts.c.user_id == user_id).order_by(accounts.c.account_id)
    accounts_output = conn.execute(query).mappings().all()
    return accounts_output


@app.post('/inspect_transactions', tags=['admin_actions'])
def get_transactions_of_account(account_id: int, admin: UserBase = Depends(get_current_admin)) -> list[dict]:
    query = select(transactions).where(transactions.c.account_id == account_id)
    transactions_output = conn.execute(query).mappings().all()
    return transactions_output


@app.post("/payment", tags=['payment'])
def generate_payment(payment: Payment) -> Union[Payment, dict]:
    test_signature = sha256((str(payment.account_id) + str(payment.amount) + payment.transaction_id + str(payment.user_id) + payment_secret_key).encode())

    if allow_empty_signature and payment.signature == '':
        payment.signature = test_signature.hexdigest()
    
    if test_signature.hexdigest() != payment.signature:
        raise HTTPException(status_code=400, detail='Invalid signature')

    query = select(transactions).where(transactions.c.transaction_id == payment.transaction_id)
    transaction_output = conn.execute(query).mappings().all()

    if transaction_output:
        raise HTTPException(status_code=400, detail='Invalid transaction id. Transaction id duplicate')
    
    query = select(users).where(users.c.user_id == payment.user_id)
    user_output = conn.execute(query).mappings().all()

    if not user_output:
        raise HTTPException(status_code=400, detail='Invalid user id. No such user')
    else:
        if user_output[0]['user_type'] != 0:
            raise HTTPException(status_code=400, detail='Invalid user type. Must be regular user')

    query = select(accounts).where(accounts.c.account_id == payment.account_id, accounts.c.user_id == payment.user_id)
    accounts_output = conn.execute(query).mappings().all()

    if not accounts_output:
        query = select(accounts).where(accounts.c.account_id == payment.account_id)
        accounts_output = conn.execute(query).mappings().all()

        if accounts_output:
            # account exists, but user_id is not bound to it
            raise HTTPException(status_code=400, detail='Invalid account id. User does not have access to this account')
        
        else:
            previous_balance = 0
            query = accounts.insert().values(
                account_id=payment.account_id,
                user_id=payment.user_id,
                balance=0
            )
            do_and_commit(query)
    else:
        previous_balance = accounts_output[0]['balance']
    
    query = accounts.update().where(accounts.c.account_id == payment.account_id).values(
        balance=previous_balance + payment.amount
    )

    do_and_commit(query)

    query = transactions.insert().values(
        transaction_id=payment.transaction_id,
        user_id=payment.user_id,
        account_id=payment.account_id,
        amount=payment.amount,
        signature=payment.signature
    )

    do_and_commit(query)
    return payment
