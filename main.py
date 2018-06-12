from flask import Flask, render_template, url_for, redirect
# Работа с формами
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
# Работа с базой данных
from flask_sqlalchemy import SQLAlchemy
# Работа с e-mail
from flask_mail import Mail, Message
# Модуль с конфеденциальной информацией 
import mymodule

app = Flask(__name__)

app.config['SECRET_KEY'] = mymodule.secret_key
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = mymodule.heroku_db

# Инфа здесь - https://yandex.ru/support/mail/mail-clients.xml
app.config['MAIL_SERVER']='smtp.yandex.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = mymodule.mail_username
app.config['MAIL_PASSWORD'] = mymodule.mail_password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
db = SQLAlchemy(app)

# Форма
class MyForm(FlaskForm):
    text_form = StringField('Your message:', validators=[DataRequired()])

# База данных
class YourMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_db = db.Column(db.String(200), nullable=False)

db.create_all()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/sport', methods=('GET', 'POST'))
def sport():
	name = mymodule.fullname
	return render_template('sport.html', name=name)

@app.route('/blog')
def blog():
	result = YourMessage.query.all()
	result.reverse() # Обратный порядок
	return render_template('blog.html', result=result)

@app.route('/message')
def message():
	form = MyForm()
	return render_template('message.html', form=form)

# Обработка формы
@app.route('/process', methods=['POST'])
def process():
	form = MyForm()

	text = form.text_form.data
	temp = YourMessage(text_db=text)

	db.session.add(temp)
	db.session.commit()

	# Если данные успешно переданы, отправить сообщение на e-mail
	if form.validate_on_submit():
		# print(form.text_form.data)
		msg = Message('Заголовок', sender = mymodule.mail_username, recipients = ['and.rey.q@yandex.ru'])
		msg.body = f"Текст сообщения:\n{form.text_form.data}"
		mail.send(msg)
	return redirect('/blog')

@app.route('/help')
def help():
	return render_template('help.html')

if __name__ == '__main__':
	app.run(debug=True)