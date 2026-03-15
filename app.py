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
            """ + "".join([f'<option value="{i}"{' selected' if i == 2 else ''}>{i}</option>' for i in range(1, 6)]) + """
        </select>
        <label for="rounds">Rounds:</label>
        <select id="rounds" name="rounds">
            """ + "".join([f'<option value="{i}"{' selected' if i == 12 else ''}>{i}</option>' for i in range(1, 101)]) + """
        </select>
        <label for="men">Men:</label>
        <select id="men" name="men">
            """ + "".join([f'<option value="{i}"{' selected' if i == 4 else ''}>{i}</option>' for i in range(2, 21)]) + """
        </select>
        <label for="women">Women:</label>
        <select id="women" name="women">
            """ + "".join([f'<option value="{i}"{' selected' if i == 4 else ''}>{i}</option>' for i in range(2, 21)]) + """
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
        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 6px; background: #fff; max-width: 520px; margin-top: 1rem;">
            <strong>Quick calculator</strong><br>
            <label for="calcPlayersPerGender">Players per gender:</label>
            <select id="calcPlayersPerGender" style="width: 70px; margin-left: 6px;">
                """ + "".join([f'<option value="{i}">{i}</option>' for i in range(1, 21)]) + """
            </select>
            <label for="calcCourts" style="margin-left: 12px;">Courts:</label>
            <select id="calcCourts" style="width: 50px; margin-left: 6px;">
                """ + "".join([f'<option value="{i}">{i}</option>' for i in range(1, 6)]) + """
            </select>
            <button type="button" onclick="calcMinRounds()" style="margin-left: 8px;">Compute</button>
            <p id="calcResult" style="margin-top: 0.5rem;"></p>
            <p style="font-size: 0.9em; margin:2px 0;">This calculates the least rounds where each player plays equally and teammate pairings are balanced (equal genders assumed).
            If output says to play a fraction of a round, use that fraction of the courts for the final round. EG: If the result is 12.5 rounds for 2 courts, use 12 2-court rounds and only one court for the final round.</p>
        </div>
        <p>Balance note: if men and women differ then exact equal game count between genders will not be achievable, this will become dramatically exagerated as the difference increases past 1.
        In this case you may want to balance the gender distribution by having a man enter as a woman or vice versa.</p>
    </section>
    <hr>
    <h3>URL-based interface</h3>
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
    <p>
        <br><br>        
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

        function calcMinRounds() {
            var playersPerGender = parseInt(document.getElementById('calcPlayersPerGender').value, 10);
            var courts = parseInt(document.getElementById('calcCourts').value, 10);
            if (isNaN(playersPerGender) || playersPerGender < 2) {
                document.getElementById('calcResult').innerHTML = 'Please select a valid number of players per gender (≥2).';
                return;
            }
            if (isNaN(courts) || courts < 1) {
                document.getElementById('calcResult').innerHTML = 'Please select a valid number of courts (≥1).';
                return;
            }

            // goal: same games per player and same teammate distribution with equal genders
            // games_per_player = (2 * courts * rounds) / playersPerGender
            // require integer, and require at least playersPerGender rounds for teammate coverage
            var rounds = 1;

            // Ensure games_per_player integer
            while ((2 * courts * rounds) % playersPerGender !== 0) {
                rounds += 1;
            }
            // Calculate games per player at this round count
            var gamesPerPlayer = (2 * courts * rounds) / playersPerGender;
            
            // Calculate number of rounds for even teammate coverage:
            var minRoundsForTeammateCoverage = rounds * (playersPerGender / gamesPerPlayer);
            while (Math.ceil(minRoundsForTeammateCoverage * courts) !== minRoundsForTeammateCoverage * courts)
            {
                minRoundsForTeammateCoverage *= 2;
            }

            document.getElementById('calcResult').innerHTML =
                'Number of rounds for even game distribution: <strong>' + rounds + '</strong> ' +
                '(yeilds ' + gamesPerPlayer + ' games per player with ' + courts + ' courts and ' + (2 * playersPerGender) + ' total players).'
                 + '<br>Minimum rounds for even teammate coverage: <strong>' + minRoundsForTeammateCoverage + '</strong> (each player plays ' + (2 * courts * minRoundsForTeammateCoverage) / playersPerGender + ' games total)';
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