from functools import wraps
from hashlib import sha256

from sanic import Sanic
from sanic.response import json, html
from sanic_jinja2 import SanicJinja2

from sqlalchemy import select

from database import create_engine_and_tables
from models import Base, UserBase, AccountBase, TransactionBase
from app_config import admin_password, admin_cookie, secret_key


conn, meta = create_engine_and_tables()
app = Sanic('async_app')
jinja = SanicJinja2(app, pkg_name="main")


def do_and_commit(query):
    try:
        conn.execute(query)
    except:
        conn.rollback()
        raise
    else:
        conn.commit()


def check_request_for_authorization_status(request):
    flag = False
    user = None
    users = meta.tables['users']

    if request.method == 'POST':
        email = request.form.get('auth_email')
        password = request.form.get('auth_pass')

        query = select(users).where(users.c.email == email, users.c.password == password)
        u = conn.execute(query).mappings().all()

        if u:
            flag = True
            user = u[0]

    return flag, user


def authorized(f):
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        is_authorized, user = check_request_for_authorization_status(request)

        if is_authorized:
            # the user is authorized.
            # run the handler method and return the response
            response = await f(request, user, *args, **kwargs)
            return response
        else:
            # the user is not authorized.
            # return html template with authorization form
            return jinja.render('authentication.html', request)

    return decorated_function


@app.route("/", methods=['GET', 'POST'])
@authorized
async def login(request, user=None):
    if user['user_type'] == 1:
        # admin panel
        response = jinja.render('admin_panel.html', request, user=user)
        response.add_cookie('password', value=admin_cookie, httponly=True)

        return response

    # user response
    response = {'user_id': user['user_id'], 'email': user['email'], 'full_name': user['full_name']}

    accounts = meta.tables['accounts']
    query = select(accounts).where(accounts.c.user_id == user['user_id']).order_by(accounts.c.account_id)
    accounts_output = conn.execute(query).mappings().all()
    
    transactions = meta.tables['transactions']
    query = select(transactions).where(transactions.c.user_id == user['user_id'])
    transactions_output = conn.execute(query).mappings().all()
    
    return jinja.render('user_panel.html', request, user=user, accounts=accounts_output, transactions=transactions_output)


def check_for_admin_cookie(f):
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        if request.cookies.get('password') == admin_cookie:
            return await f(request,*args, **kwargs)

    return decorated_function


@app.route("/admin_action", methods=['POST'])
@check_for_admin_cookie
async def admin_action(request):
    users = meta.tables['users']
    accounts = meta.tables['accounts']
    transactions = meta.tables['transactions']

    if 'add_user_submit' in request.form:
        user_id = request.form.get('user_id')
        query = select(users).where(users.c.user_id == user_id)
        result = conn.execute(query).mappings().all()

        try:
            int(user_id)
        except ValueError:
            return html('<h1>Недопустимый id пользователя! Должно быть число</h1>')

        if int(user_id) < 0:
            return html('<h1>Недопустимый id пользователя! Id должен быть > 0</h1>')

        if not result:
            query = users.insert().values(
                user_id=request.form.get('user_id'),
                email=request.form.get('email'),
                full_name=request.form.get('full_name'),
                password=request.form.get('password'),
                user_type=int(request.form.get('user_type'))
            )
        else:
            query = users.update().where(users.c.user_id == user_id).values(
                email=request.form.get('email'),
                full_name=request.form.get('full_name'),
                password=request.form.get('password'),
                user_type=int(request.form.get('user_type'))
            )
        
        do_and_commit(query)
        
        return html('<h1>Пользователь добавлен/обновлен успешно!</h1>')
    
    elif 'delete_user_submit' in request.form:
        user_id = request.form.get('user_id')
        query = select(users).where(users.c.user_id == user_id)
        result = conn.execute(query).mappings().all()

        if not result:
            return html('<h1>Пользователь не найден!</h1>')

        query = users.delete().where(users.c.user_id == request.form.get('user_id'))
        do_and_commit(query)

        query = accounts.delete().where(accounts.c.user_id == request.form.get('user_id'))
        do_and_commit(query)

        query = transactions.delete().where(transactions.c.user_id == request.form.get('user_id'))
        do_and_commit(query)

        return html('<h1>Пользователь и его счета удалены успешно!</h1>')
    
    elif "list_users_submit" in request.form:
        query = select(users).order_by(users.c.user_id)
        users_output = conn.execute(query).mappings().all()
        return jinja.render('user_list.html', request, users=users_output)
    
    elif 'get_accounts_submit' in request.form:
        try:
            int(request.form.get('user_id'))
        except ValueError:
            return html('<h1>Недопустимый id пользователя! Должно быть число</h1>')

        query = select(accounts).where(accounts.c.user_id == request.form.get('user_id')).order_by(accounts.c.account_id)
        accounts_output = conn.execute(query).mappings().all()
        return jinja.render('account_list.html', request, accounts=accounts_output)
    
    elif 'get_transactions_submit' in request.form:
        try:
            int(request.form.get('account_id'))
        except ValueError:
            return html('<h1>Недопустимый id счета! Должно быть число</h1>')
        query = select(transactions).where(transactions.c.account_id == request.form.get('account_id'))
        transactions_output = conn.execute(query).mappings().all()
        return jinja.render('transaction_list.html', request, transactions=transactions_output)

    return html('<h1>Пользователь добавлен/обновлен/удален успешно!</h1>')


def generate_payement(f):
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        if request.method == 'GET':
            return jinja.render('payment.html', request)

        if request.method == 'POST':
            try:
                int(request.form.get('user_id'))
            except ValueError:
                return json({'error': 'Wrong user id (not int)'})
            
            try:
                int(request.form.get('account_id'))
            except ValueError:
                return json({'error': 'Wrong account id (not int)'})
            
            try:
                int(request.form.get('amount'))
            except ValueError:
                return json({'error': 'Wrong amount (not int)'})

            if request.form.get('signature') is not None:
                signature = request.form.get('signature')
            else:
                signature = sha256((request.form.get('account_id') + request.form.get('amount') + request.form.get('transaction_id') + request.form.get('user_id') + secret_key).encode()).hexdigest()
            
            obj = {}
            obj['transaction_id'] = request.form.get('transaction_id')
            obj['user_id'] = int(request.form.get('user_id'))
            obj['account_id'] = int(request.form.get('account_id'))
            obj['amount'] = int(request.form.get('amount'))
            obj['signature'] = signature

            return await f(request, obj=obj)

    return decorated_function


@app.route("/payment", methods=['GET', 'POST'])
@generate_payement
async def pay(request, obj=None):
    response = obj
    test_signature = sha256((str(obj['account_id']) + str(obj['amount']) + obj['transaction_id'] + str(obj['user_id']) + secret_key).encode())

    if test_signature.hexdigest() != obj['signature']:
        return json({'error': 'Invalid signature'})
    
    if obj['amount'] <= 0:
        return json({'error': 'Invalid amount'})
    
    transactions = meta.tables['transactions']
    query = select(transactions).where(transactions.c.transaction_id == obj['transaction_id'])
    transaction_output = conn.execute(query).mappings().all()

    if transaction_output:
        return json({'error': 'Invalid transaction id'})
    
    users = meta.tables['users']
    query = select(users).where(users.c.user_id == obj['user_id'])
    user_output = conn.execute(query).mappings().all()

    if not user_output:
        return json({'error': 'Invalid user id'})
    else:
        if user_output[0]['user_type'] != 0:
            return json({'error': 'Invalid user type'})

    accounts = meta.tables['accounts']
    query = select(accounts).where(accounts.c.account_id == obj['account_id'], accounts.c.user_id == obj['user_id'])
    accounts_output = conn.execute(query).mappings().all()

    if not accounts_output:
        query = select(accounts).where(accounts.c.account_id == obj['account_id'])
        accounts_output = conn.execute(query).mappings().all()

        if accounts_output:
            # account exists, but user_id is not bound to it
            return json({'error': 'Duplicate account id (wrong user_id bound to account)'})
        
        else:
            previous_balance = 0
            query = accounts.insert().values(
                account_id=obj['account_id'],
                user_id=obj['user_id'],
                balance=0
            )
            do_and_commit(query)
    else:
        previous_balance = accounts_output[0]['balance']
    
    query = accounts.update().where(accounts.c.account_id == obj['account_id']).values(
        balance=previous_balance + obj['amount']
    )

    do_and_commit(query)

    query = transactions.insert().values(
        transaction_id=obj['transaction_id'],
        user_id=obj['user_id'],
        account_id=obj['account_id'],
        amount=obj['amount'],
        signature=obj['signature']
    )
    do_and_commit(query)
    return json(response)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
