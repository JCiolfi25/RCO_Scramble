# Flask app
from flask import Flask, request
from markupsafe import escape
from html_table_writer import write_html_table
import GraphTheory

app = Flask(__name__)

@app.route('/')
def home():
    return_html_str = """
    <h2>Simple Tourney Scheduler</h2>
    <p>
        <strong>Generate a 12 round, 2 court RCO scramble schedule:</strong><br>
        <code>/TourneyGen/&lt;num_each_gender&gt;</code><br>
        Example: <a href="https://rco-scramble.onrender.com/TourneyGen/3">https://rco-scramble.onrender.com/TourneyGen/3</a> (3 men, 3 women)
    </p>
    <p>
        <strong>Generate a schedule with custom courts and rounds:</strong><br>
        <code>/TourneyGen/&lt;courts&gt;/&lt;rounds&gt;/&lt;num_each_gender&gt;</code><br>
        Example: <a href="https://rco-scramble.onrender.com/TourneyGen/2/10/6">https://rco-scramble.onrender.com/TourneyGen/2/10/6</a> (2 courts, 10 rounds, 6 men, 6 women)
    </p>
    <p>
        <strong>Specify men and women separately:</strong><br>
        <code>/TourneyGen/&lt;courts&gt;/&lt;rounds&gt;/&lt;num_men&gt;/&lt;num_women&gt;</code><br>
        Example: <a href="https://rco-scramble.onrender.com/TourneyGen/1/12/3/2">https://rco-scramble.onrender.com/TourneyGen/1/12/3/2</a> (1 court, 12 rounds, 3 men, 2 women)
    </p>
    <p>
        If num_gender = num_men = num_women, and (num_games * 2) // num_gender = 0, then everyone will play the same number of games.
    </p>
    <hr>
    <h3>Custom Schedule Generator</h3>
    <form id="tourneyForm" onsubmit="event.preventDefault(); goToSchedule();">
        <label for="courts">Courts:</label>
        <select id="courts" name="courts">
            """ + "".join([f'<option value="{i}">{i}</option>' for i in range(1, 6)]) + """
        </select>
        <label for="rounds">Rounds:</label>
        <select id="rounds" name="rounds">
            """ + "".join([f'<option value="{i}">{i}</option>' for i in range(1, 101)]) + """
        </select>
        <label for="men">Men:</label>
        <select id="men" name="men">
            """ + "".join([f'<option value="{i}">{i}</option>' for i in range(2, 21)]) + """
        </select>
        <label for="women">Women:</label>
        <select id="women" name="women">
            """ + "".join([f'<option value="{i}">{i}</option>' for i in range(2, 21)]) + """
        </select>
        <button type="submit">Go</button>
    </form>
    <script>
        function goToSchedule() {
            var courts = document.getElementById('courts').value;
            var rounds = document.getElementById('rounds').value;
            var men = document.getElementById('men').value;
            var women = document.getElementById('women').value;

            // Use /TourneyGen/<courts>/<rounds>/<num_men>/<num_women>
            window.location.href = `/TourneyGen/${courts}/${rounds}/${men}/${women}`;
        }
    </script>
    """
    return return_html_str

@app.route('/hello')
#http://127.0.0.1:5000/hello?name=John
def hello_name():
    name=request.args.get("name","Flask")
    return f"Hello, {escape(name)}!"

@app.route('/healthy')
#http://127.0.0.1:5000/healthy
def healthy():
    return "Healthy!"

@app.route('/int/<int:num>')
#http://127.0.0.1:5000/int/55
def do_math(num):
    return f"The square of {num} is {num**2}!"

@app.route('/TourneyGen/<int:num_each_gender>')
def TourneyGenGendersMatch(num_each_gender):
    scheddy = GraphTheory.Main(num_men=num_each_gender)
    return scheddy.ReturnHTMLSchedule()

@app.route('/TourneyGen/<int:courts>/<int:rounds>/<int:num_each_gender>')
def TourneyGenCourtsRoundsGendersMatch(courts, rounds, num_each_gender):
    scheddy = GraphTheory.Main(num_courts=courts, num_rounds=rounds, num_men=num_each_gender)
    return scheddy.ReturnHTMLSchedule()

@app.route('/TourneyGen/<int:courts>/<int:rounds>/<int:num_men>/<int:num_women>')
def TourneyGenCourtsRoundsMenWomen(courts, rounds, num_men, num_women):
    scheddy = GraphTheory.Main(num_courts=courts, num_rounds=rounds, num_men=num_men, num_women=num_women)
    return scheddy.ReturnHTMLSchedule()

# headers = ["Name", "Age", "City"]
# rows = [["Alice", 30, "Boston"], ["Bob", 27, "Chicago"]]
# html_str = write_html_table("report.html", headers, rows, title="Employee Report")

# To run, activate the .venv then run "flask run" in the terminal. Then visit http://127.0.0.1:5000