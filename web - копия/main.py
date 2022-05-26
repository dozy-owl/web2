from flask import Flask
from flask import render_template, request
import requests
from bs4 import BeautifulSoup
from flask_login import LoginManager
from flask_login import login_user, logout_user
from flask_login import login_required
from flask_login import current_user
from flask import abort

from constants import *
from log import *
from countries_top import create_table, show_country
from forms.user import RegisterForm
from forms.news import NewsForm
from forms.answers import AnswerForm
from data.news import News
from data.answers import Answers

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ec69284899e36ea86429f41e15f808a7o'


login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader


def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Зелёный Дом')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/pollution_level', methods=['GET', 'POST'])
def pollution_level():
    answer = "86	Россия	9.3	145934460"
    if request.method == "POST":
        country = request.form['country']
        answer = show_country(country)
    return render_template('pollution_level.html',
                           title='Зелёный Дом. Уровень\
                           загрязнения окружающей среды',
                           table=create_table(), answer=answer)


@app.route('/garbage_and_society')
def garbage_and_society():
    return render_template('garbage_and_society.html',
                           title='Зелёный Дом. Отходы и общество')


@app.route('/environmental_protection')
def environmental_protection():
    return render_template('environmental_protection.html',
                           title='Зелёный Дом. Охрана окружающей среды')


@app.route('/dirty_cities')
def dirty_cities():
    return render_template('dirty_cities.html',
                           title='Зелёный Дом. Самые "грязные" города России',
                           krasnoyarsk=KRASNOYARSK, magnitogorsk=MAGNITOGORSK,
                           norilsk=NORILSK, lipetsk=LIPETSK,
                           cherepovets=CHEREPOVETS, novokuznetsk=NOVOKUZNETSK,
                           nizhny_tagil=NIZHNY_TAGIL, omsk=OMSK,
                           chelyabinsk=CHELYABINSK, dzerzhinsk=DZERZHINSK,
                           bratsk=BRATSK, chita=CHITA, mednogorsk=MEDNOGORSK,
                           novocherkassk=NOVOCHERKASSK, asbestos=ASBESTOS)


@app.route('/people')
def people():
    return render_template('people.html',
                           title='Зелёный Дом. Лица,\
                           ответственные за экологию в России')


@app.route('/indicators')
def indicators():
    return render_template('indicators.html',
                           title='Зелёный Дом. Основные показатели\
                           экологии России')


@app.route('/rbk_news')
def rbk_news():
    response = requests.get(URL)
    if response.status_code == 200:
        stitle = []
        stext = []
        sdate = []
        soup = BeautifulSoup(response.content, "html.parser")
        text_all = soup.find_all("div", class_=CLASS_TEXT_ALL)
        for i in text_all:
            if "search-item__text" in str(i):
                i = str(i).split()
                date = i[i.index('class="search-item__category">') + 1:
                         i.index('</span>')]
                date = ' '.join(date)
                title = i[i.index('class="search-item__link-in">') + 2:
                          i.index('class="search-item__text">') - 1]
                title[0] = title[0][title[0].find('>') + 1:]
                title[-1] = title[-1][:title[-1].find('<')]
                title = ' '.join(title)
                i = i[i.index('class="search-item__text">') + 1:]
                text = i[: i.index('</span>')]
                text = ' '.join(text)
                stitle.append(title)
                stext.append(text)
                sdate.append(date)
        return render_template('rbk_news.html', n=len(stitle),
                               titles=stitle,
                               texts=stext, dates=sdate,
                               title='Зелёный Дом. Новости')


@app.route("/public")
def public():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
               (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("public.html", news=news[::-1],
                           title='Зелёный Дом. Обсуждения')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(
               User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/public')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/public')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    answers = db_sess.query(Answers).filter(Answers.news_id == id).all()
    if news:
        db_sess.delete(news)
        for answer in answers:
            db_sess.delete(answer)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/public')


@app.route('/answers/<int:id>',  methods=['GET', 'POST'])
@login_required
def news_answer(id):
    form = AnswerForm()
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id).first()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        ans = Answers()
        ans.title = form.title.data
        ans.content = form.content.data
        ans.news_id = news.id
        current_user.ans.append(ans)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/answers/{id}')
    anss = db_sess.query(Answers).filter(Answers.news_id == id).all()
    return render_template('anss.html', form=form, news_title=news.title,
                           news_content=news.content, news_name=news.user.name,
                           news_date=news.created_date, answers=anss[::-1],
                           title=f'Обсуждение. {news.title}')


@app.route('/answers_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def answers_delete(id):
    db_sess = db_session.create_session()
    answer = db_sess.query(Answers).filter(
             Answers.id == id,
             Answers.user == current_user).first()
    if answer:
        db_sess.delete(answer)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/public')


@app.route('/answer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news_answer(id):
    form = AnswerForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        ans = db_sess.query(Answers).filter(
              Answers.id == id,
              Answers.user == current_user).first()
        if ans:
            form.title.data = ans.title
            form.content.data = ans.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        ans = db_sess.query(Answers).filter(
              Answers.id == id,
              Answers.user == current_user).first()
        if ans:
            ans.title = form.title.data
            ans.content = form.content.data
            db_sess.commit()
            return redirect(f'/answer/{id}')
        else:
            abort(404)
    return render_template('anss.html',
                           title='Редактирование ответа',
                           form=form)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')
