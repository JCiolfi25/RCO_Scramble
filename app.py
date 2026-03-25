# Flask app
from flask import Flask, request, redirect, url_for
from markupsafe import escape
from html_table_writer import write_html_table
import GraphTheory

app = Flask(__name__)

global g_num_men, g_num_women,g_names_men, g_names_women, g_courts, g_rounds
g_num_men = None
g_num_women = None
g_names_men = None
g_names_women = None
g_courts = None
g_rounds = None

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
            <label for="calcPlayersMen">Number of Men:</label>
            <select id="calcPlayersMen" style="width: 70px; margin-left: 6px;">
                """ + "".join([f'<option value="{i}"{' selected' if i == 4 else ''}>{i}</option>' for i in range(2, 21)]) + """
            </select>
            <label for="calcPlayersWomen" style="margin-left: 12px;">Number of Women:</label>
            <select id="calcPlayersWomen" style="width: 70px; margin-left: 6px;">
                """ + "".join([f'<option value="{i}"{' selected' if i == 6 else ''}>{i}</option>' for i in range(2, 21)]) + """
            </select>
            <label for="calcCourts" style="margin-left: 12px;">Courts:</label>
            <select id="calcCourts" style="width: 50px; margin-left: 6px;">
                """ + "".join([f'<option value="{i}"{' selected' if i == 2 else ''}>{i}</option>' for i in range(1, 6)]) + """
            </select>
            <button type="button" onclick="calcMinRounds()" style="margin-left: 8px;">Compute</button>
            <p id="calcResult" style="margin-top: 0.5rem;"></p>
            <p style="font-size: 0.9em; margin:2px 0;">This calculates the minimum number of rounds where players within a gender all play the same number of games.
            If output says to play a fraction of a round, use that fraction of the courts for the final round. EG: If the result is 12.5 rounds for 2 courts, use 12 2-court rounds and only one court for the final round.
            If the minimum number of rounds is less than you want to play, scale up as desired by multiples of this minimum value. 
            If the genders are unbalanced, you can manually add in some single-gender games to help balance games between genders.
            For guideline on how many points to play to, divide total desired time (in minutes) by number of rounds to play (eg if you have 3 hours to play 12 rounds then play to 15 points, as 180 min/12 rounds = 15.</p>
        </div>
        <p>Balance note: if men and women differ then exact equal game count between genders will not be achievable, this will become dramatically exagerated as the difference increases past 1.
        In this case you may want to balance the gender distribution by having a man enter as a woman or vice versa.</p>
    </section>
    <hr>
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
        function calcMinGamesHelper(numPlayers) {
            var playersPerGender = numPlayers;
            // games_per_player = (2 * courts * rounds) / playersPerGender
            // require integer number of games, and require at least playersPerGender rounds for teammate coverage
            var games = 1;

            // Ensure games_per_player integer
            while ((2 * games) % playersPerGender !== 0) {
                games += 1;
            }
            return games;
        }
        function findMinRounds(minGamesMen, minGamesWomen, numCourts) {
            let lar = Math.max(minGamesMen, minGamesWomen);
            let small = Math.min(minGamesMen, minGamesWomen);
            var done = false;
            var i = lar;
            var gamesLCM = 0;
            while (done == false) {
                if (i % small == 0) {
                    done = true;
                    gamesLCM = i;
                }
                i += lar;
            }
            return Math.trunc(100 * gamesLCM / numCourts)/100;
        }
        function calcMinRounds() {
            var playersMen = parseInt(document.getElementById('calcPlayersMen').value, 10);
            var playersWomen = parseInt(document.getElementById('calcPlayersWomen').value, 10);
            var courts = parseInt(document.getElementById('calcCourts').value, 10);
            if (isNaN(playersMen) || playersMen < 2 || isNaN(playersWomen) || playersWomen < 2) {
                document.getElementById('calcResult').innerHTML = 'Please select a valid number of players per gender (≥2).';
                return;
            }
            if (isNaN(courts) || courts < 1) {
                document.getElementById('calcResult').innerHTML = 'Please select a valid number of courts (≥1).';
                return;
            }
            if (courts * 2 > playersMen || courts * 2 > playersWomen) {
                document.getElementById('calcResult').innerHTML = 'Not enough players for the selected number of courts. ' +
                    'Two players of each gender required per court.';
                return;
            }
            var minGamesMen = calcMinGamesHelper(playersMen);
            var minGamesWomen = calcMinGamesHelper(playersWomen);

            var minRounds = findMinRounds(minGamesMen, minGamesWomen, courts);
            document.getElementById('calcResult').innerHTML =
                'Total rounds should be a multiple of <strong>' + minRounds + '</strong> ' +
                '(Every ' + minRounds + ' rounds, each man plays ' + Math.round((2 * courts * minRounds) / playersMen) + ' games and each woman plays ' + Math.round((2 * courts * minRounds) / playersWomen) + ' games)';
        }
    </script>
    """
    return return_html_str


@app.route('/TourneyGen/<int:courts>/<int:rounds>/<int:num_men>/<int:num_women>')
def TourneyGenCourtsRoundsMenWomen(courts, rounds, num_men, num_women):
# Target from /home Javascript; sets the globals and then rediirects to MakeTourney to get names entered
    global g_num_men, g_num_women, g_courts, g_rounds
    g_num_men = num_men
    g_num_women = num_women
    g_courts = courts
    g_rounds = rounds
    return redirect(url_for('EnterPlayerNames'))

@app.route('/PlayerNames', methods=['GET', 'POST'], strict_slashes=False)
# Allows entry of player names
def EnterPlayerNames():
    global g_num_men, g_num_women, g_courts, g_rounds
    if g_num_men is None or g_num_women is None or g_courts is None or g_rounds is None:
        return redirect(url_for('home'))
    # Render form to get player names
    if request.method == 'GET':
        form_html = f"""
        <h2>Enter Player Names</h2>
        <h3>Men:</h3>
        <form method="post">
            {''.join([f'<input type="text" name="man_{i}" placeholder="Man{i+1}" title="Only letters, numbers, spaces, underscores, and hyphens allowed."><br>' for i in range(g_num_men)])}
        <h3>Women:</h3>
            {''.join([f'<input type="text" name="woman_{i}" placeholder="Woman{i+1}" title="Only letters, numbers, spaces, underscores, and hyphens allowed."><br>' for i in range(g_num_women)])}
            <button type="submit">Go</button>
        </form>
        """
        return form_html
    # Handle form submission
    elif request.method == 'POST':
        import re
        names_men = []
        names_women=[]
        for i in range(g_num_men):
            name = request.form.get(f'man_{i}')
            if name is None or len(name) == 0 or len(name.strip()) == 0:
                name = f"Man{i+1}"
            else: name = name.strip()
            if not re.fullmatch(r'[A-Za-z0-9 _-]{1,32}', name):
                return f"Invalid name for Man {i+1}: '{name}'. Only letters, numbers, spaces, underscores, and hyphens allowed. Max 32 characters."
            names_men.append(name)
        for i in range(g_num_women):
            name = request.form.get(f'woman_{i}')
            if name is None or len(name) == 0 or len(name.strip()) == 0:
                name = f"Woman{i+1}"
            else: name = name.strip()
            if not re.fullmatch(r'[A-Za-z0-9 _-]{1,32}', name):
                return f"Invalid name for Woman {i+1}: '{name}'. Only letters, numbers, spaces, underscores, and hyphens allowed. Max 32 characters."
            names_women.append(name)

    global g_names_men, g_names_women
    g_names_men = names_men
    g_names_women = names_women
    return redirect(url_for('TourneyGenNames'))

@app.route('/TourneyGenNames')
def TourneyGenNames():
    # Creates the actual tourney with the names provided from globals
    global g_names_men, g_names_women, g_courts, g_rounds
    if g_names_men is None or g_names_women is None or g_courts is None or g_rounds is None:
        return redirect(url_for('home'))
    scheddy = GraphTheory.Main(names_men=g_names_men, names_women=g_names_women, num_courts=g_courts, num_rounds=g_rounds)
    return scheddy.ReturnHTMLSchedule()

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

# To run, activate the .venv then run "flask run" in the terminal. Then visit http://127.0.0.1:5000