# Flask app
from flask import Flask, request
from markupsafe import escape
from html_table_writer import write_html_table
import GraphTheory

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

@app.route('/home')
def home():
    return_str = """Simple tourney scheduler. Visit /TourneyTest/num to 
    generate a 12 round, 2 court RCO scramble schedule with num men and num women;
    for 2 courts, 12 rounds, 3 men, and 3 women:\n
    https://rco-scramble.onrender.com/TourneyTest/3
\n
    Visit /TourneyTest/courts/rounds/num to generate court Courts, round Rounds schedule
    with num men and num women;
    For 2 courts, 10 rounds, 6 men, and 6 women:
    https://rco-scramble.onrender.com/TourneyTest/2/10/6
    
    Or /TourneyTest/courts/rounds/num_men/num_women to specify more parameters;
    for 1 court, 12 rounds, 3 men, 2 women:
    https://rco-scramble.onrender.com/TourneyTest/1/12/3/2
    
    if num_gender=num_men=num_women, and num_games*2 // num_gender = 0,
    then everyone will play the same number of games
    """
    return return_str

@app.route('/hello')
#http://127.0.0.1:5000/hello?name=John
def hello_name():
    name=request.args.get("name","Flask")
    return f"Hello, {escape(name)}!"


@app.route('/int/<int:num>')
#http://127.0.0.1:5000/int/55
def do_math(num):
    return f"The square of {num} is {num**2}!"

@app.route('/TourneyTest/<int:num_each_gender>')
def TourneyTestGendersMatch(num_each_gender):
    scheddy = GraphTheory.Main(num_men=num_each_gender)
    return scheddy.ReturnHTMLSchedule()

@app.route('/TourneyTest/<int:courts>/<int:rounds>/<int:num_each_gender>')
def TourneyTestCourtsRoundsGendersMatch(courts, rounds, num_each_gender):
    scheddy = GraphTheory.Main(num_courts=courts, num_rounds=rounds, num_men=num_each_gender)
    return scheddy.ReturnHTMLSchedule()

@app.route('/TourneyTest/<int:courts>/<int:rounds>/<int:num_men>/<int:num_women>')
def TourneyTestCourtsRoundsMenWomen(courts, rounds, num_men, num_women):
    scheddy = GraphTheory.Main(num_courts=courts, num_rounds=rounds, num_men=num_men, num_women=num_women)
    return scheddy.ReturnHTMLSchedule()

# headers = ["Name", "Age", "City"]
# rows = [["Alice", 30, "Boston"], ["Bob", 27, "Chicago"]]
# html_str = write_html_table("report.html", headers, rows, title="Employee Report")

# To run, activate the .venv then run "flask run" in the terminal. Then visit http://127.0.0.1:5000