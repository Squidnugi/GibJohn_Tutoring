import requests
from flask import Flask, render_template, request, make_response
from flask_navigation import Navigation
import sqlite3
import random
from werkzeug.security import check_password_hash, generate_password_hash

print("http://localhost:5000/")
app = Flask(__name__)
nav = Navigation(app)
# checks server connection
conn = sqlite3.connect('identifier.sqlite')
print('👍')
conn.close()
# list of api links
Geography = ['https://the-trivia-api.com/questions?categories=geography&limit=10',
             'https://opentdb.com/api.php?amount=10&category=22']  ##
History = ['https://the-trivia-api.com/questions?categories=history&limit=10',
           'https://opentdb.com/api.php?amount=10&category=23']  ##
Science = ['https://the-trivia-api.com/questions?categories=science&limit=10',
           'https://opentdb.com/api.php?amount=10&category=17']  ##
Computers = ['https://opentdb.com/api.php?amount=10&category=18']  ##
Math = ['https://opentdb.com/api.php?amount=10&category=19']  ##
Sports = ['https://opentdb.com/api.php?amount=10&category=21']  ##
# global dictionaries
global_questions = {}
global_answers = {}
global_subject = {}

# items on the navbar
nav.Bar('top', [
    nav.Item('GibJohn Tutoring', 'home'),
    nav.Item('Subjects', 'subjects'),
    nav.Item('Sign Out', 'sign_out'),
])


# checks if there is a user logged in
def logged_in_checker():
    username = request.cookies.get('User_name')
    correct = False
    with sqlite3.connect('identifier.sqlite') as con:
        cur = con.execute('SELECT username FROM users')
        for i in cur:
            if username == i[0]:
                correct = True
    return correct


# welcome and home page
@app.route('/', methods=['GET', 'POST'])
def home():
    # collects data from the database for the "Times Complete" and "Times 100%" leaderboard
    def get_subjects(list_subs, list_subjects):
        subjects = {'Geography': 0, 'History': 0, 'Science': 0, 'Computers': 0, 'Math': 0, 'Sports': 0}  ##
        with sqlite3.connect('identifier.sqlite') as con:
            get_ID = con.execute('SELECT ID, username FROM users')
            for i in get_ID:
                if i[1] == username:
                    ID = i[0]
            val = con.execute(
                f'SELECT {list_subs[0]}, {list_subs[1]}, {list_subs[2]}, {list_subs[3]}, {list_subs[4]}, {list_subs[5]} FROM users WHERE ID = {ID}')  ##
            for i in val:
                for x in range(0, 6):  ##
                    subjects[list_subjects[x]] = i[x]
        sorted_subjects = sorted(subjects.items(), key=lambda x: x[1], reverse=True)
        return sorted_subjects

    # checks for cookie
    username = request.cookies.get('User_name')
    correct = False
    with sqlite3.connect('identifier.sqlite') as con:
        cur = con.execute('SELECT username FROM users')
        for i in cur:
            if username == i[0]:
                correct = True
    if correct:
        list_subjects = ['Geography', 'History', 'Science', 'Computers', 'Math', 'Sports']  ##
        list_comp_subjects = ['Geography_comp', 'History_comp', 'Science_comp', 'Computers_comp', 'Math_comp',
                              'Sports_comp']  ##
        # collects users for leaderboard
        users = []
        with sqlite3.connect('identifier.sqlite') as con:
            cur = con.execute('SELECT username, xp FROM users ORDER BY xp DESC')
            for i in cur:
                temp = []
                for x in i:
                    temp.append(x)
                users.append(temp)
        subs_done = get_subjects(list_subjects, list_subjects)
        subs_comp = get_subjects(list_comp_subjects, list_subjects)
        return render_template('index.html', username=username, users=users, subjects=subs_done, subs_comp=subs_comp)
    else:
        return render_template('welcome.html')


# link to sign out page
@app.route('/sign_out')
def sign_out():
    correct = logged_in_checker()
    if correct:
        return render_template('sign-out.html')


# link to sign-up page
@app.route('/sign_up', methods=['GET'])
def sign_up():
    return render_template('sign-up.html')


# link to the bye page
@app.route('/bye', methods=['POST'])
def bye():
    if request.method == 'POST':
        # removes cookie to logout user
        resp = make_response(render_template('bye.html'))
        resp.set_cookie('User_name', '', expires=0)
        return resp


# link to login page
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


# function behind the sign-up page
@app.route('/signed_up', methods=['POST'])
def signed_up():
    if request.method == 'POST':
        try:
            # grabs data from input
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            password = generate_password_hash(password)
            # inputs data into database
            with sqlite3.connect('identifier.sqlite') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)", (username, email, password))

                con.commit()
                msg = "Account successfully created"

                resp = make_response(render_template("success.html", msg=msg, username=username))
                resp.set_cookie('User_name', username)

                return resp
        except:
            con.rollback()
            msg = "Error: Username or email might already exist or invalid data"
            return render_template("success.html", msg=msg)


# function behind the login page
@app.route('/logged_in', methods=['POST'])
def logged_in():
    if request.method == 'POST':
        try:
            # collects data from input
            username = request.form['username']
            password = request.form['password']

            # collects data from database and compares it to the users input
            with sqlite3.connect('identifier.sqlite') as con:
                cur = con.execute('SELECT username,password, email FROM users')
                correct = False
                email_username = ''
                for i in cur:
                    if username == i[0] or username == i[2]:
                        if check_password_hash(i[1], password):
                            correct = True
                            email_username = i[0]
                if correct == True:
                    msg = "Successfully logged in"
                    resp = make_response(render_template("success.html", msg=msg, username=email_username))
                    resp.set_cookie('User_name', value=email_username, max_age=604800)  # 604800 is a week in seconds

                    return resp
                else:
                    msg = "Username or password incorrect"
                    return render_template("success.html", msg=msg)
        except:
            con.rollback()
            msg = "error"
            return render_template("success.html", msg=msg)


# function behind subject page
@app.route('/subjects')
def subjects():
    correct = logged_in_checker()
    if correct:
        # creates the names of each quiz
        def list_creator(sub, name):
            slist = []
            num = len(sub)
            while num != 0:
                temp = name + "Quiz" + str(num)
                slist.append(temp)
                num -= 1
            slist.sort()
            return slist

        glist = list_creator(Geography, 'G')  ##
        hlist = list_creator(History, 'H')  ##
        sclist = list_creator(Science, 'Sc')  ##
        clist = list_creator(Computers, 'C')  ##
        mlist = list_creator(Math, 'M')  ##
        splist = list_creator(Sports, 'Sp')  ##
        return render_template('subjects.html', Geography=glist, History=hlist, Science=sclist, Computers=clist,
                               Math=mlist,
                               Sports=splist)  ##


@app.route('/quiz/<int:id>', methods=['POST', 'GET'])
def quiz(id):
    username = request.cookies.get('User_name')
    if id == 0:  ##
        # looks for subject
        val = request.form['subject']
        if 'G' in val:  ##
            num = len(val) - 1
            subject = Geography[int(val[num]) - 1]
            sub = 'Geography'  ##
        elif 'H' in val:  ##
            num = len(val) - 1
            subject = History[int(val[num]) - 1]
            sub = 'History'  ##
        elif 'Sc' in val:  ##
            num = len(val) - 1
            subject = Science[int(val[num]) - 1]
            sub = 'Science'  ##
        elif 'C' in val:  ##
            num = len(val) - 1
            subject = Computers[int(val[num]) - 1]
            sub = 'Computers'  ##
        elif 'M' in val:  ##
            num = len(val) - 1
            subject = Math[int(val[num]) - 1]
            sub = 'Math'  ##
        elif 'Sp' in val:  ##
            num = len(val) - 1
            subject = Sports[int(val[num]) - 1]
            sub = 'Sports'  ##
        # checks for api
        if 'opentdb.com' in subject:
            questions = open_api(subject)
            api = 'open'
        elif 'the-trivia-api.com' in subject:
            questions = triv_api(subject)
            api = 'triv'
        global_questions[username] = questions
        global_subject[username] = sub
        global_answers[username] = []
    elif id == 10:  ##
        answer = request.form['optradio']
        global_answers[username].append(answer)
        result = 0
        for i in global_answers[username]:
            if i == 'correct':
                result += 1
        # caluates score
        score = result * 10
        if result == 10:
            addxp = 1000
            hundred = 1
            comp = 1
        elif result == 0:
            addxp = 10
            hundred = 0
            comp = 0
        else:
            addxp = score
            hundred = 0
            comp = 1
        # adds calues to the database
        with sqlite3.connect('identifier.sqlite') as con:
            cur = con.cursor()
            subject = global_subject[username]
            complete = global_subject[username] + '_comp'
            ID = get_id(username)
            add = con.execute(f'SELECT xp, {subject}, {complete} FROM users WHERE ID = {ID}')
            for i in add:
                xp = i[0]
                sub = i[1]
                sub_comp = i[2]
            xp += addxp
            sub += comp
            sub_comp += hundred
            cur.execute(f'UPDATE users SET xp = {xp}, {subject} = {sub}, {complete} = {sub_comp} WHERE ID = {ID}')
        return render_template('results.html', score=score)

    else:
        answer = request.form['optradio']
        global_answers[username].append(answer)
    rand = random.randint(1, 4)
    return render_template('questions.html', questions=global_questions[username][id], next=id + 1, pos=rand)


# gets the id of the user
def get_id(username):
    with sqlite3.connect('identifier.sqlite') as con:
        num = 0
        temp = con.execute('SELECT ID, username FROM users')
        for i in temp:
            if i[1] == username:
                num = i[0]
    return num


# filters question of known errors in the string and gets data from api
def open_api(subject):
    response = requests.get(subject)
    api = response.json()
    questions = api['results']
    loop = 0
    for i in questions:
        result1 = i['question'].replace('&#039;', "'")
        result2 = result1.replace('&quot;', '"')
        questions[loop]['question'] = result2
        loop += 1
    final = []
    # filters the data into used setup
    for i in questions:
        temp = {}
        temp['question'] = i['question']
        temp['correct_answer'] = i['correct_answer']
        temp['incorrect_answers'] = i['incorrect_answers']
        final.append(temp)
    return final


# gets data from api
def triv_api(subject):
    response = requests.get(subject)
    api = response.json()
    final = []
    # filters the data into used setup
    for i in api:
        temp = {}
        temp['question'] = i['question']
        temp['correct_answer'] = i['correctAnswer']
        temp['incorrect_answers'] = i['incorrectAnswers']
        final.append(temp)
    return final



if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)
