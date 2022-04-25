import requests
from flask import Flask, render_template, request, make_response
from flask_bootstrap import Bootstrap
from flask_navigation import Navigation
from jinja2 import Template
import sqlite3
import time
import random
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

temp = {}

#https://opentdb.com/
#catagories:
#21 = Sports
#17 = Science & Nature
#18 = Computers
#19 = Maths
#22 = Geography
#23 = History
#
def open_trivia_api():
    response = requests.get('https://opentdb.com/api.php?amount=10&category=21&difficulty=easy&type=multiple')
    api = response.json()
    #print(api)
    questions = api['results']
    print(questions[1]['question'])
    for i in questions:
        result1 = i['question'].replace('&#039;', "'")
        result2 = result1.replace('&quot;', '"')
        print(result2)
    # for i in questions:
        # print(i)
        # print(i['category'])
        # print(i['type'])
        # print(i['difficulty'])
        # print(i['question'])
        # print(i['correct_answer'])
        # print(i['incorrect_answers'])

#https://the-trivia-api.com/
def The_Trivia_API():
    response = requests.get('https://the-trivia-api.com/questions?categories=sport&leisure&limit=10')
    api = response.json()
    #print(api)
    # print()
    # for i in api:
    #     print(i['question'])
    print(len(api))

@app.route('/')
def test1():
    val = 'Hi'
    return render_template('test.html', something=True, val=val)

@app.route('/test', methods=['POST'])
def test2():
    if request.method == 'POST':
        val = request.form['val']
        return render_template('test.html', something=False, val=val)

def test():
    with sqlite3.connect('identifier.sqlite') as con:
        num = 0
        passward = con.execute('SELECT password FROM users WHERE ID = 5')
        for i in passward:
            print(i[0])
            print(check_password_hash(i[0],'Password123'))

if __name__ == '__main__':
    test()
    #app.run()
    #The_Trivia_API()
    # print('the-trivia-api.com' in 'https://the-trivia-api.com/questions?categories=sport&leisure&limit=10')
    # print('opentdb.com' in 'https://opentdb.com/api.php?amount=10&category=21&difficulty=easy&type=multiple')