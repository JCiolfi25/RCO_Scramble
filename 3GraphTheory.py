# Seems to be correctly implementing byes, as well as printing schedule with limited number of courts 
# Also implemented optional numCourts to be passed to Edge.Cull() to select that many games with lowest weights; if numCourts is unspecified and therefore None, it will select as many games as possible without repeating teams
#       Unsure if Edge.Cull() should ever actually be passed numCourts; if it is, those "extra" games from that round will be thrown out and those other teams won't be used.  As of now, those "extra" games just get bumped to the next round.
#        Believe I need some kind of scoring algorithm for tournament_history.csv to determine which algorithm is better for creating overall schedule

# Butters: "Weighted Undirected Complete Graph"
# The graph is even after every LCM(N, N-1) rounds, where N is the number of men and also the number of women
# With number of men/women not divisible by 2, it gets wonky; need to add a heuristic to even out the number of games played by each player (could use len of teammates as proxy for games played)
    # Maybe, when calculating edge weights, add something like 0.001 per teammate each person has had in that edge, to encourage more even distribution of games played among players
import csv
import itertools
from datetime import datetime

class AlgoParams:
    def __init__(self, repeat_exponential, opponent_history_weight, teammate_history_weight, games_played_weight, cull_num_courts):
        self.repeat_exponential = repeat_exponential # Exponent applied to number of repeats when calculating edge weights, to make further repeats heavier; can be adjusted to make the algorithm more or less averse to repeats
        self.opponent_history_weight = opponent_history_weight # Weight added to edge for each time a player in a team on the edge has already played against that opponent (non-reciprocal)
        self.teammate_history_weight = teammate_history_weight  # Weight added to edge for each time a player in a team on the edge has already played with that teammate
        self.games_played_weight = games_played_weight # Weight added to edge for each game a player in a team on the edge has played (tracked as number of past teammates), to encourage more even distribution of games played among players
        # Note games_played_weight is essentially multiplied by 4 because it's counted per player

        self.cull_num_courts = cull_num_courts
        # if true, Round.Cull() will be passed numCourts to select that many games with lowest weights; 
        # if false, Round.Cull() will select as many games as possible without repeating teams and all games will be passed into the schedule (games that don't fit will pass to next round)

    def Print(self):
        print(f"Algorithm Parameters:")
        print(f"  Repeat Exponential: {self.repeat_exponential}")
        print(f"  Opponent History Weight: {self.opponent_history_weight}")
        print(f"  Teammate History Weight: {self.teammate_history_weight}")
        print(f"  Games Played Weight: {self.games_played_weight}")
        print(f"  Cull Num Courts: {self.cull_num_courts}")
class Player:
    def __init__(self, name):
        self.name = name
        self.is_man = None
        self.past_teammates = list()  
        self.past_opponents = list()
        self.repeat_teammates = 0
        self.repeat_opponents = 0
        self.games_played = 0
    def Print(self, include_history=False, include_stats=False):
        print(f"Player: {self.name}")
        if include_history:
            print(f"  Past Teammates: {[p.name for p in self.past_teammates]}")
            print(f"  Past Opponents: {[p.name for p in self.past_opponents]}")
        if include_stats:
            print(f"  Games Played: {self.games_played}")
            print(f"  Repeat Teammates: {self.repeat_teammates}")
            print(f"  Repeat Opponents: {self.repeat_opponents}")
    def UpdateStats(self):
        self.past_opponents.sort(key=lambda p: p.name)
        self.past_teammates.sort(key=lambda p: p.name)
        self.repeat_teammates = len(self.past_teammates) - len(set(self.past_teammates))
        self.repeat_opponents = len(self.past_opponents) - len(set(self.past_opponents))
        self.games_played = len(self.past_teammates) # Using number of past teammates as a proxy for games played, since each game adds exactly one teammate
class Team:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.name = f"{player1.name}/{player2.name}"
    def Print(self):
        print(f"Team: {self.player1.name} & {self.player2.name}")
class Round:
    def __init__(self, teams):
        self.teams = teams # (Team1, Team2, ...)
        self.edges = list()
        self.isWeighted = False
        self.isCulled = False
        for teams in itertools.combinations(teams, 2):
            self.edges.append(Edge(*teams, 0))
    def Print(self, print_edges=False):
        print("Round:")
        for team in self.teams:
            team.Print()
        if print_edges:
            print("Edges:")
            for edge in self.edges:
                print(f"  {edge.team1.name} - {edge.team2.name}: {edge.weight}")
    def WeightEdges(self, algo_params):
        for edge in self.edges:
            edge.WeightSelf(algo_params)
        self.isWeighted = True
    def Cull(self, numCourts=None): # Select games with lowest weights; if numCourts is specified, select that many games; otherwise, select as many games as possible without repeating teams
        # Round.Cull() returns the list of games to be played this round, based on edge weights
        self.edges.sort(key=lambda e: e.weight)
        selected_games = list()
        used_teams = set()
        for edge in self.edges:
            if edge.team1 not in used_teams and edge.team2 not in used_teams:
                selected_games.append(Game(edge.team1, edge.team2))
                used_teams.add(edge.team1)
                used_teams.add(edge.team2)
                if len(selected_games) == numCourts: # if numCourts is unspecified and therefore None, this condition will never be true and it will select as many games as possible without repeating teams; if numCourts is specified, it will select that many games
                    break
        self.isCulled = True
        return selected_games
class Edge:
    def __init__(self, team1, team2, weight):
        self.team1 = team1
        self.team2 = team2
        self.weight = weight
    def WeightSelf(self, algo_params):
        # Calculate weight based on past interactions
        p1, p2 = self.team1.player1, self.team1.player2
        p3, p4 = self.team2.player1, self.team2.player2
        # For each time a player has played another player, add opponent_history_weight to the weight; squared so further repeats are heavier
        self.weight += p3.past_opponents.count(p1)**algo_params.repeat_exponential * algo_params.opponent_history_weight
        self.weight += p4.past_opponents.count(p1)**algo_params.repeat_exponential * algo_params.opponent_history_weight
        self.weight += p3.past_opponents.count(p2)**algo_params.repeat_exponential * algo_params.opponent_history_weight
        self.weight += p4.past_opponents.count(p2)**algo_params.repeat_exponential * algo_params.opponent_history_weight
        
        # For each time a player has played with a teammate, add teammate_history_weight to the weight; squared so further repeats are heavier
        self.weight += p1.past_teammates.count(p2)**algo_params.repeat_exponential * algo_params.teammate_history_weight
        self.weight += p3.past_teammates.count(p4)**algo_params.repeat_exponential * algo_params.teammate_history_weight
        # For each game a player has played (tracked as number of past teammates), add games_played_weight to the weight to encourage more even distribution of games played among players
        for p in [p1, p2, p3, p4]:
            self.weight += algo_params.games_played_weight * len(p.past_teammates)
class Game:
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2
    def Print(self):
        print(f"Game: {self.team1.name} vs {self.team2.name}")
class Schedule:
    def __init__(self, numCourts=None):
        self.games=list()
        self.numCourts = numCourts
    def AddGame(self, game):
        # Schedule.AddGame(game) also updates the relevant players' past teammates and opponents lists
        self.games.append(game)
        # Update past teammates and opponents for each player in the game
        (P1, P2, P3, P4) = (game.team1.player1, game.team1.player2, game.team2.player1, game.team2.player2)
        P1.past_teammates.append(P2)
        P1.past_opponents.extend([P3, P4])
        P1.UpdateStats()
        P2.past_teammates.append(P1)
        P2.past_opponents.extend([P3, P4])
        P2.UpdateStats()
        P3.past_teammates.append(P4)
        P3.past_opponents.extend([P1, P2])
        P3.UpdateStats()
        P4.past_teammates.append(P3)
        P4.past_opponents.extend([P1, P2])
        P4.UpdateStats()
    def Print(self):
        print("Schedule:")
        for game in self.games:
            print(f"  {game.team1.name} vs {game.team2.name}")
    def ExportHistoryCSV(self, filename="tournament_history.csv"):
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Game", "Player", "Teammate", "Opponent1", "Opponent2"])
            game_num = 1
            for game in self.games:
                (A,B,C,D) = (game.team1.player1, game.team1.player2, game.team2.player1, game.team2.player2)
                writer.writerow([game_num, A.name, B.name, C.name, D.name])
                writer.writerow([game_num, B.name, A.name, C.name, D.name])
                writer.writerow([game_num, C.name, D.name, A.name, B.name])
                writer.writerow([game_num, D.name, C.name, A.name, B.name])
                game_num += 1
    def ExportScheduleCSV(self, filename="tournament_schedule.csv"):
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            if self.numCourts == None:# or self.numCourts == 1:
                writer.writerow(["Game", "Team1", "Team2"])
                game_num = 1
                for game in self.games:
                    writer.writerow([game_num, game.team1.name, game.team2.name])
                    game_num += 1
            else:
                header = ["Round"]
                for i in range(self.numCourts):
                    header.extend([f"Court {i+1} Team1", f"Court {i+1} Team2"])
                # header.extend([*(f"Court {i+1} Team1", f"Court {i+1} Team2") for i in range(self.numCourts)])
                writer.writerow(header)
                game_num = 1
                row = list([1]) # Start with round 1
                for game in self.games:
                    row.extend([game.team1.name, game.team2.name])
                    if game_num % self.numCourts == 0:
                        writer.writerow(row)
                        row = list([game_num//self.numCourts + 1])
                    game_num += 1
                if len(row) > 1:
                    writer.writerow(row)

def PrintStats(players, algo_params, num_rounds=None, num_courts=None, num_games=None, print_individuals=False, print_overall=False, csv_append=False):
    list_repeat_teammates_nums = list()
    list_repeat_opponents_nums = list()
    list_games_played_nums = list()
    num_men = len([p for p in players if p.is_man])
    num_women = len([p for p in players if not p.is_man])
    for player in players:
        player.UpdateStats()
        list_repeat_teammates_nums.append(player.repeat_teammates)
        list_repeat_opponents_nums.append(player.repeat_opponents)
        list_games_played_nums.append(player.games_played)
        if print_individuals: 
            player.Print(include_history=True, include_stats=True)
    if print_overall:
        print("")
        print("Repeat Opponents per player Overall:\n\tMin: \t{},\n\tMax: \t{},\n\tAvg: \t{}".format(min(list_repeat_opponents_nums), max(list_repeat_opponents_nums), sum(list_repeat_opponents_nums)/len(list_repeat_opponents_nums)))
        print("Repeat Teammates per player Overall:\n\tMin: \t{},\n\tMax: \t{},\n\tAvg: \t{}".format(min(list_repeat_teammates_nums), max(list_repeat_teammates_nums), sum(list_repeat_teammates_nums)/len(list_repeat_teammates_nums)))
        print("Games Played per player Overall:\n\tMin: \t{},\n\tMax: \t{},\n\tAvg: \t{}".format(min(list_games_played_nums), max(list_games_played_nums), sum(list_games_played_nums)/len(list_games_played_nums)))
        # if num_games is not None:
        #     print(f"Optimal for {num_games} total games and {len(players)} total players - ")
        #     print(f"\tMinimum possible teammate repeats per player, assuming equal men and women: {num_games//(len(players)/2-1)}") # Each player can have at most (number of players/2 - 1) unique teammates, assuming equal men and women
        #     print(f"\tMinimum possible opponent repeats per player, assuming equal men and women: {num_games//(len(players)/2)}") # Each player can have at most (number of players) unique opponents, assuming equal men and women
        #     print(f"\tOptimal games played per player: {num_games/(len(players)/4)}") # Each game involves 4 players, so optimal games played per player is total games divided by (number of players / 4)
    if csv_append:
        with open("tournament_stats.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            stats = [datetime.now(), num_rounds, num_courts, num_men, num_women, num_games, min(list_repeat_opponents_nums), max(list_repeat_opponents_nums), sum(list_repeat_opponents_nums)/len(list_repeat_opponents_nums), min(list_repeat_teammates_nums), max(list_repeat_teammates_nums), sum(list_repeat_teammates_nums)/len(list_repeat_teammates_nums), min(list_games_played_nums), max(list_games_played_nums), sum(list_games_played_nums)/len(list_games_played_nums)]
            algo = [algo_params.cull_num_courts, algo_params.repeat_exponential, algo_params.opponent_history_weight, algo_params.teammate_history_weight, algo_params.games_played_weight]
            writer.writerow(stats + algo)

def GeneratePlayers(num_men, num_women=None):
    """Generates the players based on number of men and women

    Args:
        num_men (int): The number of men to generate.
        num_women (int, optional): The number of women to generate. If not given, will default to num_men

    Returns:
        players_men, players_women: (list players, list players): The generated men and women players.
    """
    if num_women is None:
        num_women = num_men
    players_men = list()
    for i in range(num_men):
        players_men.append(Player(f"M{i+1}"))
        players_men[i].is_man = True
    players_women = list()
    for i in range(num_women):
        players_women.append(Player(f"W{i+1}"))
        players_women[i].is_man = False
    return players_men, players_women

def GenerateTeamsByRound(num_rounds, players_men, players_women):
    """Generates teams by round deterministically. Requires N rounds to ensure that each player has played with every other player of the opposite gender at least once, where N is equal to greater of num_men or num_women

    Args:
        num_rounds (int): The number of rounds to generate teams for.
        players_men (list of players): The list of men players.
        players_women (list of players): The list of women players.

    Returns:
        rounds_all_teams: A list of lists of teams, where each inner list represents the teams for a round.
    """
    rounds_all_teams = list()
    for r in range(num_rounds):
        n_len = len(players_men)
        # Rotate women to create unique partners
        rotated_women = players_women[r%n_len:] + players_women[:r%n_len]
        next_round_teams = list()
        for team in (zip(players_men, rotated_women)):
            next_round_teams.append(Team(*team))
        rounds_all_teams.append(next_round_teams)
    return rounds_all_teams

def GenerateSchedule(rounds_all_teams, algo_params, num_courts=None, num_rounds_sched=None):
    """Generates the schedule based on the teams for each round and the algorithm parameters

    Args:
        rounds_all_teams (list of lists of teams): A list of lists of teams, where each inner list represents the teams for a round.
        algo_params (AlgoParams): The parameters for the pairing algorithm used to choose games per round.
        num_courts (int, optional): The number of courts available for scheduling games. If not given, will default to None, which means unlimited courts (i.e. as many games as possible per round without repeating teams).
        num_rounds_sched (int, optional): The number of rounds to generate the schedule for. If not given, will default to None, which means it will generate for all rounds in rounds_all_teams.

    Returns:
        scheddy: The generated Schedule object containing the scheduled games.
    """
    if num_rounds_sched is None:
        num_rounds_sched = len(rounds_all_teams)
    rounds=list()
    for round in rounds_all_teams:
        rounds.append(Round(round))
    scheddy = Schedule(numCourts=num_courts)
    even_round_numbers = list() #???
    games_added = 0
    for i in range(len(rounds)):
        # print(f"=== ROUND {i+1} ===")
        round = rounds[i]
        round.WeightEdges(algo_params=algo_params)
        # round.Print(print_edges=True)
        round_weights = [edge.weight for edge in round.edges]
        if len(set(round_weights)) == 1:
            even_round_numbers.append(i+1)
        for game in round.Cull(numCourts=(num_courts if algo_params.cull_num_courts else None)): # If numCourts is None, it will select as many games as possible without repeating teams; if numCourts is specified, it will select that many games
            if num_courts == None or (games_added < num_courts * num_rounds_sched): # Only add up to num_courts * num_rounds games to the schedule, since that's the maximum that can be played in the given number of rounds and courts; if num_courts is None, this condition will never be true and it will add all games
                # game.Print()
                scheddy.AddGame(game)
                games_added += 1
    return scheddy

def Main(num_rounds, num_courts, algo_params, num_men, num_women=None):
    players_men, players_women = GeneratePlayers(num_men, num_women) # if one number given, assumes that many men and that many women
    rounds_all_teams = GenerateTeamsByRound(num_rounds=num_rounds, players_men=players_men, players_women=players_women)
    
    scheddy = GenerateSchedule(num_rounds_sched = num_rounds, num_courts = num_courts, rounds_all_teams=rounds_all_teams, algo_params=algo_params)
    scheddy.ExportHistoryCSV()
    scheddy.ExportScheduleCSV()

    PrintStats(players = players_men + players_women, algo_params=algo_params, print_individuals=False, num_courts=num_courts, num_rounds=num_rounds, print_overall=True, csv_append=True)

    print("Done")

if __name__ == "__main__":
    algo_params = AlgoParams(repeat_exponential=2, opponent_history_weight=1, teammate_history_weight=0.001, games_played_weight=10, cull_num_courts=True)
    num_rounds= 12
    num_courts = 2
    Main(num_rounds=num_rounds, num_courts=num_courts, algo_params=algo_params, num_men=5)
    