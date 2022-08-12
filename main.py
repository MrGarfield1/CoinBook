import os

from flask import Flask, render_template, request, flash, url_for, redirect, session
import pypyodbc
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './static/img/user_images'

connection = pypyodbc.connect('Driver={SQL Server};'
                              'Server=;'
                              'Database=Монеты;')
cursor = connection.cursor()

app = Flask(__name__)
app.config['SECRET_KEY'] = ''

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def start():
    return render_template('start.html')


@app.route("/profile/<username>", methods=["POST", "GET"])
def profile(username):
    if 'username' in session:
        print('Пользователь авторизован')
        print(session['username'])
    llist = [session['username']]
    cursor.execute("SELECT DISTINCT Страна FROM Монеты WHERE ИДПользователя=?", llist)
    country_money = cursor.fetchall()
    cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
    name = str(cursor.fetchall()[0][0])
    if request.method == 'POST':
        llist = []
        if request.form['year_before'] == '':
            llist.append(None)
        else:
            llist.append(request.form['year_before'])
        if request.form['year_after'] == '':
            llist.append(None)
        else:
            llist.append(request.form['year_after'])
        if request.form['price_before'] == '':
            llist.append(None)
        else:
            llist.append(request.form['price_before'])
        if request.form['price_after'] == '':
            llist.append(None)
        else:
            llist.append(request.form['price_after'])
        if request.form['country'] == '':
            llist.append(None)
        else:
            llist.append(request.form['country'])
        if request.form['nominal'] == '':
            llist.append(None)
        else:
            llist.append(request.form['nominal'])
        print(llist)
        cursor.execute("EXEC Фильтр_категорий ?, ?, ?, ?, ?, ?", llist)
        list_money = cursor.fetchall()
        print(list_money)
        llist = [session['username']]
        cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
        name = str(cursor.fetchall()[0][0])
        if list_money:
            return render_template('profile.html', money=list_money, name=name, country=country_money,
                                   year_before=request.form['year_before'], year_after=request.form['year_after'],
                                   price_before=request.form['price_before'], price_after=request.form['price_after'],
                                   country_money=request.form['country'], nominal=request.form['nominal'])
        else:
            flash('Такой монеты нет', category='error')
    return render_template('profile.html', money=get_money(username), name=name, country=country_money,
                           country_money=get_country(username))


def get_country(username):
    print(username)
    cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", [session['username']])
    name = str(cursor.fetchall()[0][0])
    if username == name:
        return ""
    else:
        return username


def get_money(username):
    print(username)
    cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", [session['username']])
    name = str(cursor.fetchall()[0][0])
    if username == name:
        llist = [session['username']]
        cursor.execute("SELECT ИДМонеты, Название, Страна, Год, Тираж, Материал, Диаметр, Цена, Фото FROM Монеты "
                       "WHERE ИДПользователя=? ORDER BY ИДМонеты DESC", llist)
        list_money = cursor.fetchall()
        return list_money
    else:
        llist = [session['username'], username]
        cursor.execute("SELECT ИДМонеты, Название, Страна, Год, Тираж, Материал, Диаметр, Цена, Фото FROM Монеты "
                       " WHERE ИДПользователя=? AND Страна=? ORDER BY ИДМонеты DESC", llist)
        list_money = cursor.fetchall()
        return list_money


@app.route("/registration", methods=["POST", "GET"])
def registration():
    try:
        if request.method == 'POST':
            llist = [request.form['username'], request.form['email'], request.form['password']]
            cursor.execute("INSERT INTO [Пользователи] VALUES (?, ?, ?)", llist)
            connection.commit()
            return redirect(url_for('start'))
        return render_template('registration.html')
    except:
        flash('Что-то пошло не так', category='error')
        return render_template('registration.html')


@app.route("/login", methods=["POST", "GET"])
def entrance():
    if request.method == 'POST':
        llist = [request.form['email'], request.form['password']]
        info = cursor.execute("SELECT * FROM Пользователи WHERE Email=? and Пароль=?", llist)

        if info.fetchone() is None:
            flash('Такого пользователя нет или ошибка в логине или пароле', category='error')
        else:
            llist = [request.form['email']]
            cursor.execute("SELECT ИДПользователя FROM Пользователи WHERE Email=?", llist)
            session['username'] = int(cursor.fetchall()[0][0])

            cursor.execute("SELECT Имя FROM Пользователи WHERE Email=?", llist)
            name = str(cursor.fetchall()[0][0])
            return redirect(url_for(f'profile', username=name))
    return render_template('login.html')


@app.route("/profile/newmoney", methods=["POST", "GET"])
def newmoney():
    try:
        if request.method == 'POST':
            llist = [session['username'], request.form['name']]
            file = request.files['img']
            file.filename = str(session['username']) + '_' + str(request.form['name']) + '.' + str(
                file.filename.rsplit('.', 1)[1].lower())
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            llist = [session['username'], request.form['name'], request.form['country'], request.form['year'],
                    request.form['circulation'], request.form['material'], request.form['diameter'],
                    request.form['price'], request.form['post'], str('img/user_images/') + str(filename)]
            cursor.execute("INSERT INTO [Монеты] VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", llist)
            connection.commit()
            llist = [session['username']]
            cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
            return redirect(url_for('profile', username=str(cursor.fetchall()[0][0])))
        llist = [session['username']]
        cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
        return render_template('newmoney.html', name=str(cursor.fetchall()[0][0]))
    except:
        llist = [session['username']]
        cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
        flash('Что-то пошло не так', category='error')
        return render_template('newmoney.html', name=str(cursor.fetchall()[0][0]))


@app.route("/post/<int:id_money>")
def showDescription(id_money):
    llist = [int(id_money)]
    cursor.execute("SELECT ИДПользователя FROM Монеты WHERE ИДМонеты=?", llist)
    id_user = int(cursor.fetchall()[0][0])
    if id_user == session['username']:
        cursor.execute("SELECT Описание FROM Монеты WHERE ИДМонеты=?", llist)
        description = str(cursor.fetchall()[0][0])
        llist = [session['username']]
        cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
        name = str(cursor.fetchall()[0][0])
        return render_template('money.html', money=description, name=name)
    else:
        llist = [session['username']]
        cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
        return redirect(url_for('profile', username=str(cursor.fetchall()[0][0])))


@app.route("/post/<int:id_money>/delete")
def delete(id_money):
    llist = [int(id_money)]
    cursor.execute("DELETE FROM [Монеты] WHERE ИДМонеты=?", llist)
    connection.commit()
    llist = [session['username']]
    cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
    name = str(cursor.fetchall()[0][0])
    return redirect(url_for('profile', username=name))


@app.route("/post/<int:id_money>/update", methods=["POST", "GET"])
def update(id_money):
    try:
        if request.method == 'POST':
            file = request.files['img']
            print(file.filename)
            file.filename = str(session['username']) + '_' + str(request.form['name']) + '.' + str(
                file.filename.rsplit('.', 1)[1].lower())
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            llist = [session['username'], request.form['name'], request.form['country'], request.form['year'],
                     request.form['circulation'], request.form['material'], request.form['diameter'],
                     request.form['price'], request.form['post'], str('img/user_images/') + str(filename), id_money]
            cursor.execute("UPDATE [Монеты] SET ИДПользователя=?, Название=?, Страна=?, Год=?, Тираж=?, Материал=?, "
                           "Диаметр=?, Цена=?, Описание=?, Фото=? WHERE ИДМонеты=?", llist)
            connection.commit()
            llist = [session['username']]
            cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
            return redirect(url_for('profile', username=str(cursor.fetchall()[0][0])))
        llist = [session['username'], id_money]
        cursor.execute("SELECT * FROM Монеты WHERE ИДПользователя=? AND ИДМонеты=?", llist)
        money = cursor.fetchall()[0]
        llist = [session['username']]
        cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
        return render_template('newmoney_update.html', user_name=str(cursor.fetchall()[0][0]), name=money[2],
                               country=money[3], year=money[4], circulation=money[5], material=money[6],
                               diameter=money[7], price=money[8], post=money[9], img=money[10], id_money=money[0])
    except:
        llist = [session['username'], id_money]
        cursor.execute("SELECT * FROM Монеты WHERE ИДПользователя=? AND ИДМонеты=?", llist)
        money = cursor.fetchall()[0]
        flash('Что-то пошло не так', category='error')
        llist = [session['username']]
        cursor.execute("SELECT Имя FROM Пользователи WHERE ИДПользователя=?", llist)
        return render_template('newmoney_update.html', user_name=str(cursor.fetchall()[0][0]),
                               name=money[2], country=money[3], year=money[4], circulation=money[5], material=money[6],
                               diameter=money[7], price=money[8], post=money[9], img=money[10], id_money=money[0])


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('start'))


if __name__ == '__main__':
    app.run(debug=True)
