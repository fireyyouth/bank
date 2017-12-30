from flask import Flask, make_response, request, render_template, g
import sqlite3


app = Flask(__name__)
def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        g.db = sqlite3.connect('bank.db')
        g.db.row_factory = sqlite3.Row
    return g.db
@app.route('/')
def admin():
    return render_template('admin.html', \
            users = get_db().cursor().execute('select *from user').fetchall())
@app.route('/<uid>', methods=['GET', 'POST'])
def index(uid):
    cursor = get_db().cursor()
    user = cursor.execute('select *from user where id = ?', (uid,)).fetchone()
    if user == None:
        return 'no such uid'
    else:
        if request.method == 'POST' and request.form.get('to'):
            #verify form['amount'] is an int
            amount = 0
            try:
                amount = int(request.form.get('amount'))
            except:
                return 'amount is not a number'
            #verify target id exists
            if cursor.execute('select *from user where id = ?',\
                    (request.form['to'],)).fetchone() == None:
                        return 'no such target id'
            #verify fund is enough
            if cursor.execute('select *from user where id = ?',\
                    (uid,)).fetchone()['money'] < amount:
                        return 'insufficient fund'
            #make transfer
            cursor.execute('update user set money = money - ? where id = ?', \
                    (amount, uid))
            cursor.execute('update user set money = money + ? where id = ?', \
                    (amount, request.form['to']))
            get_db().commit();
        user = cursor.execute('select *from user where id = ?', (uid,)).fetchone()
        return render_template('index.html', user=user)
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

app.run(debug=True)
    
