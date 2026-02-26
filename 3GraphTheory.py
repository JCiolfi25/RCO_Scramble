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

opponent_history_weight = 1 # Weight added to edge for each time a player in a team on the edge has already played against that opponent (non-reciprocal)
teammate_history_weight = 0.001 # Weight added to edge for each time a player in a team on the edge has already played with that teammate
games_played_weight = 0.001 # Weight added to edge for each game a player in a team on the edge has played (tracked as number of past teammates), to encourage more even distribution of games played among players


class Player:
    def __init__(self, name):
        self.name = name
        self.is_man = None
        self.past_teammates = list()  
        self.past_opponents = list()
    def Print(self, include_history=False):
        print(f"Player: {self.name}")
        if include_history:
            print(f"  Past Teammates: {[p.name for p in self.past_teammates]}")
            print(f"  Past Opponents: {[p.name for p in self.past_opponents]}")
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
    def WeightEdges(self):
        for edge in self.edges:
            edge.WeightSelf()
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
    def WeightSelf(self):
        # Calculate weight based on past interactions
        p1, p2 = self.team1.player1, self.team1.player2
        p3, p4 = self.team2.player1, self.team2.player2
        # For each time a player has played another player, add opponent_history_weight to the weight
        self.weight += p3.past_opponents.count(p1) * opponent_history_weight
        self.weight += p4.past_opponents.count(p1) * opponent_history_weight
        self.weight += p3.past_opponents.count(p2) * opponent_history_weight
        self.weight += p4.past_opponents.count(p2) * opponent_history_weight
        
        # For each time a player has played with a teammate, add teammate_history_weight to the weight
        self.weight += p1.past_teammates.count(p2) * teammate_history_weight
        self.weight += p3.past_teammates.count(p4) * teammate_history_weight
        # For each game a player has played (tracked as number of past teammates), add games_played_weight to the weight to encourage more even distribution of games played among players
        for p in [p1, p2, p3, p4]:
            self.weight += games_played_weight * len(p.past_teammates)
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
        P2.past_teammates.append(P1)
        P2.past_opponents.extend([P3, P4])
        P3.past_teammates.append(P4)
        P3.past_opponents.extend([P1, P2])
        P4.past_teammates.append(P3)
        P4.past_opponents.extend([P1, P2])
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
            if self.numCourts ==None or self.numCourts == 1:
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
                row = list([game_num//self.numCourts + 1])
                for game in self.games:
                    row.extend([game.team1.name, game.team2.name])
                    if game_num % self.numCourts == 0:
                        writer.writerow(row)
                        row = list([game_num//self.numCourts + 1])
                    game_num += 1
                if len(row) > 1:
                    writer.writerow(row)

if __name__ == "__main__":
    n = 4 # Number of men and also number of women
    rounds= 21
    num_courts = 1
    players_men = list()
    for i in range(n):
        players_men.append(Player(f"M{i+1}"))
        players_men[i].is_man = True
    players_women = list()
    for i in range(n):
        players_women.append(Player(f"W{i+1}"))
        players_women[i].is_man = False

    # print(players_men)
    # print(players_women)
    # print("================================")

    rounds_all_teams = list()
    for r in range(rounds):
        n_len = len(players_men)
        # Rotate women to create unique partners
        rotated_women = players_women[r%n_len:] + players_women[:r%n_len]
        next_round_teams = list()
        for team in (zip(players_men, rotated_women)):
            next_round_teams.append(Team(*team))
        rounds_all_teams.append(next_round_teams)

    # num_teams = 0
    # for i in range(len(rounds_all_teams)):
    #     round = rounds_all_teams[i]
    #     for team in round:
    #         num_teams += 1
            # team.Print()
        # print("")
    # print(num_teams)
    
    rounds=list()
    for round in rounds_all_teams:
        rounds.append(Round(round))
    scheddy = Schedule(numCourts=num_courts)
    even_round_numbers = list() #???
    for i in range(len(rounds)):
        print(f"=== ROUND {i+1} ===")
        round = rounds[i]
        round.WeightEdges()
        round.Print(print_edges=True)
        round_weights = [edge.weight for edge in round.edges]
        if len(set(round_weights)) == 1:
            even_round_numbers.append(i+1)
        for game in round.Cull():
            game.Print()
            scheddy.AddGame(game)
    scheddy.Print()
    print(even_round_numbers)
    scheddy.ExportHistoryCSV()
    scheddy.ExportScheduleCSV()



    print("Done")