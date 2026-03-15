# Flask app
from flask import Flask, request, redirect, url_for
from markupsafe import escape
from html_table_writer import write_html_table
import GraphTheory

app = Flask(__name__)

@app.route('/',strict_slashes=False)
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
    <style>
        /* Responsive form styling */
        #tourneyForm {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            max-width: 600px;
        }
        #tourneyForm label, #tourneyForm select, #tourneyForm button {
            font-size: 1em;
        }
        #tourneyForm label {
            min-width: 60px;
        }
        @media (max-width: 600px) {
            #tourneyForm {
                flex-direction: column;
                align-items: stretch;
            }
            #tourneyForm label, #tourneyForm select, #tourneyForm button {
                width: 100%;
                margin-bottom: 5px;
            }
        }
    </style>
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
        <div style="height: 60px;"></div>
    </form>
    <table style="border-collapse: collapse; width: 100%; max-width: 750px; margin-top: 1rem;">
        <thead>
            <tr>
                <th style="border: 1px solid #ccc; padding: 8px; background: #f5f5f5; text-align: left;">Parameter</th>
                <th style="border: 1px solid #ccc; padding: 8px; background: #f5f5f5; text-align: left;">Type</th>
                <th style="border: 1px solid #ccc; padding: 8px; background: #f5f5f5; text-align: left;">Description</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="border: 1px solid #ccc; padding: 8px;">courts</td>
                <td style="border: 1px solid #ccc; padding: 8px;">integer</td>
                <td style="border: 1px solid #ccc; padding: 8px;">Number of courts to schedule games on (1-5).</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ccc; padding: 8px;">rounds</td>
                <td style="border: 1px solid #ccc; padding: 8px;">integer</td>
                <td style="border: 1px solid #ccc; padding: 8px;">Number of rounds to generate (1-100).</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ccc; padding: 8px;">men</td>
                <td style="border: 1px solid #ccc; padding: 8px;">integer</td>
                <td style="border: 1px solid #ccc; padding: 8px;">Number of male players (2-20).</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ccc; padding: 8px;">women</td>
                <td style="border: 1px solid #ccc; padding: 8px;">integer</td>
                <td style="border: 1px solid #ccc; padding: 8px;">Number of female players (2-20).</td>
            </tr>
        </tbody>
    </table>
    <section style="margin-top: 1.5rem; padding: 1rem; border: 1px solid #ddd; border-radius: 6px; background: #fafafa; max-width: 750px;">
        <h4>Play count &amp; balance</h4>
        <p>Use this quick calculator logic to understand expected number of games per player.</p>
        <ul>
            <li><strong>Total players</strong> = num_men + num_women</li>
            <li><strong>Total matches</strong> = courts × rounds</li>
            <li><strong>Spots per match</strong> = 4 (RCO scramble uses 4 players per game)</li>
            <li><strong>Total player-slots</strong> = Total matches × Spots per match</li>
            <li><strong>Average games per player</strong> = Total player-slots ÷ Total players</li>
        </ul>
        <p>Example: with 2 courts, 12 rounds, 6 men, 6 women:</p>
        <p>Total matches = 24; Total player-slots = 96; Total players = 12; Average games/player = 8.</p>
        <p>Balance note: if men and women differ by &gt;1, exact equal game count may not be achievable, so fewer players may need to rotate or sit out to keep courts full.</p>
    </section>
    <p>
        Note: If the number of men and the number of women is off from each other by more than ~1, the schedule will be a bit unbalanced.
        In this case you may want to balance the gender distribtion by having a man enter as a woman or vise versa. <br><br>        
        <em>Repo for this website and the scheduler algorithm it uses:
        <a href="https://github.com/JCiolfi25/RCO_Scramble/tree/Render-deployed">https://github.com/JCiolfi25/RCO_Scramble/tree/Render-deployed</a>
        </em>
    </p>
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

@app.errorhandler(404)
# Redirect if someone tries to go to an invalid link
def page_not_found(e):
    return redirect(url_for('home'))

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