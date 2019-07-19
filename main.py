from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
import requests, json
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = "sZWjFJmyFQnzkVMxbOIAIZNJhaJV"

class LoginForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Email()])
    zuoraId = StringField("Zuora ID", validators = [DataRequired()])
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
    form = LoginForm()
    if form.validate_on_submit():
        zuoraUser = form.email.data
        zuoraPass = form.password.data
        zuoraId = form.zuoraId.data
        accountInfo = getAccountInfo(zuoraId, zuoraUser, zuoraPass).json()
        subscriptionInfo = getSubscriptionInfo(zuoraId, zuoraUser, zuoraPass).json()
        ratePlanCharges = subscriptionInfo["subscriptions"][0]["ratePlans"][0]["ratePlanCharges"]
        subscriptions = subscriptionInfo["subscriptions"][0]

        response = {}

        if "paymentTerm" in accountInfo["billingAndPayment"]:
            response["Payment Term"] = accountInfo["billingAndPayment"]["paymentTerm"]

        if "currency" in accountInfo["billingAndPayment"]:
            response["Currency"] = accountInfo["billingAndPayment"]["currency"]

        if "bookDate" in subscriptions:
            response["Book Date"] = subscriptions["bookDate"]

        if "termType" in subscriptions:
            response["Term Setting"] = subscriptions["termType"]

        if "poNumber" in subscriptions:
            response["PO Number"] = subscriptions["poNumber"]

        if "signatureDate" in subscriptions:
            response["Signature Date"] = subscriptions["signatureDate"]

        if "subscriptionEdition" in subscriptions:
            response["Subscription Edition"] = subscriptions["subscriptionEdition"]

        for ratePlanCharge in ratePlanCharges:
            if ratePlanCharge["name"] == "Milestone":
                response["Milestone, Non-billing Total"] = ratePlanCharge["nonBillingTotal"]
                response["Milestone, Total Budgeted Hours"] = ratePlanCharge["totalBudgetedHours"]
            if ratePlanCharge["name"] == "Retainer Fee":
                response["Retainer Fee, Total"] = ratePlanCharge["Total"]
            if ratePlanCharge["name"] == "Time & Materials Actuals":
                response["Time & Materials Actuals, Non-billing Total"] = ratePlanCharge["nonBillingTotal"]
                response["Time & Materials Actuals, Total Budgeted Hours"] = ratePlanCharge["totalBudgetedHours"]

        #set whatever data is retrieved to a cariable named results
        return redirect(url_for('display', zuoraData = response))
        #Do smth with the login info
    return render_template('login.html', title = 'Login', form = form)

if __name__ == '__main__':
    app.run()
