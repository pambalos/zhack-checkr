from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
import requests, json
from requests.auth import HTTPBasicAuth

class ZuoraUser:
    def setDetails(self, email, password):
        self.email = email 
        self.password = password

app = Flask(__name__)
app.config['SECRET_KEY'] = "fAkEsEcReTkEy"

zuoraAccount = ZuoraUser()




class LoginForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Email()])
    zuoraId = StringField("Zuora ID", validators = [DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit = SubmitField("Login")

class ZuoraLoginForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit = SubmitField("Login")


def getAccountInfo(accountId, username, password):
    return requests.get('https://rest.zuora.com/v1/accounts/' + accountId,
           auth=HTTPBasicAuth(username, password))


def getSubscriptionInfo(accountId, username, password):
    return requests.get('https://rest.zuora.com/v1/subscriptions/accounts/' + accountId,
           auth=HTTPBasicAuth(username, password))

@app.route('/display/<zuoraData>', methods = ["GET"])
def display(zuoraData):

    return render_template('display.html', title = 'Display', zuoraData = zuoraData)

@app.route('/', methods = ["GET", "POST"])
def home():
    form = ZuoraLoginForm()
    if form.validate_on_submit():
        zuoraAccount.setDetails(form.email.data, form.password.data)
        
        #set whatever data is retrieved to a cariable named results
        return redirect(url_for('zuoraAccountLookup', email = zuoraAccount.email, password = zuoraAccount.password))
        #Do smth with the login info
    return render_template('login.html', title = 'Login', form = form)

@app.route('/api/zlookup/<email>+<password>')
def zuoraLookup(email, password):
    return requests.post('https://rest.apisandbox.zuora.com/v1/action/query', data = json.dumps({'queryString' : 'select Id, Name from account'}), auth = HTTPBasicAuth(zuoraAccount.email, zuoraAccount.password) )

@app.route('/zuoralookup', methods = ["GET", "POST"])
def zuoraAccountLookup():
    #response = requests.post('https://rest.apisandbox.zuora.com/v1/action/query', data = json.dumps({'queryString' : 'select Id, Name from account'}), auth = HTTPBasicAuth(zuoraAccount.email, zuoraAccount.password) )
    #for item in response:
     #   print('item: ' + item)


    return render_template('lookup.html', title = "Zuora Account Lookup")

if __name__ == '__main__':
    app.run()
