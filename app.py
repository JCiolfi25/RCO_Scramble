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
    return_str = r"""Simple tourney scheduler. Visit /TourneyTest/num to 
    generate a 12 round, 2 court RCO scramble schedule with num men and num women.
    Visit /TourneyTest/courts/rounds/num to generate court Courts, round Rounds schedule
    with num men and num wome."""
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

@app.route('/TourneyTest/<int:num_men>')
def TourneyTest(num_men):
    scheddy = GraphTheory.Main(num_men=num_men)
    return scheddy.ReturnHTMLSchedule()

@app.route('/TourneyTest/<int:courts>/<int:rounds>/<int:num_each_gender>')
def TourneyTest(courts, rounds, num_each_gender):
    scheddy = GraphTheory.Main(courts=courts, rounds=rounds, num_each_gender=num_each_gender)
    return scheddy.ReturnHTMLSchedule()

# headers = ["Name", "Age", "City"]
# rows = [["Alice", 30, "Boston"], ["Bob", 27, "Chicago"]]
# html_str = write_html_table("report.html", headers, rows, title="Employee Report")
