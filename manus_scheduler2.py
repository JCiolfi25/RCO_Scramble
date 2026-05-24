import random
import copy
from collections import defaultdict
from typing import List, Dict, Tuple, Set

from html_table_writer import write_html_table

class VolleyballScheduler:
    def __init__(self, men: List[str], women: List[str], num_courts: int, num_rounds: int):
        self.men = men
        self.women = women
        self.num_courts = num_courts
        self.num_rounds = num_rounds
        
        # Tracking stats
        self.games_played = {p: 0 for p in men + women}
        # teammate_counts[(p1, p2)] = count
        self.teammate_counts = defaultdict(int)
        # opponent_counts[(p1, p2)] = count
        self.opponent_counts = defaultdict(int)
        
        self.schedule = []

    def _calculate_round_penalty(self, round_matches) -> float:
        penalty = 0.0
        for t1, t2 in round_matches:
            # Teammate repeats (M-W pairs)
            # Higher penalty for each subsequent repeat
            c1 = self.teammate_counts[tuple(sorted(t1))]
            c2 = self.teammate_counts[tuple(sorted(t2))]
            penalty += (10 ** c1) * 10000 if c1 > 0 else 0
            penalty += (10 ** c2) * 10000 if c2 > 0 else 0
            
            # Opponent repeats
            for p1 in t1:
                for p2 in t2:
                    count = self.opponent_counts[tuple(sorted((p1, p2)))]
                    penalty += (10 ** count) * 100 if count > 0 else 0
        return penalty

    def _get_neediest_players(self, players: List[str], count: int) -> List[str]:
        """
        Strictly select the players who have played the fewest games.
        If there's a tie, choose randomly among the tied players.
        """
        if count >= len(players):
            return list(players)
            
        # Group players by games played
        by_games = defaultdict(list)
        for p in players:
            by_games[self.games_played[p]].append(p)
            
        selected = []
        # Sort games played ascending
        for g in sorted(by_games.keys()):
            available = by_games[g]
            needed = count - len(selected)
            if needed <= 0:
                break
            
            if len(available) <= needed:
                selected.extend(available)
            else:
                selected.extend(random.sample(available, needed))
        return selected

    def generate(self, iterations_per_round: int = 15000):
        for r in range(1, self.num_rounds + 1):
            best_round_matches = []
            min_round_penalty = float('inf')
            
            # 1. Determine how many players we need
            needed_per_gender = 2 * self.num_courts
            actual_needed_men = min(needed_per_gender, (len(self.men) // 2) * 2, (len(self.women) // 2) * 2)
            actual_needed_women = actual_needed_men # Must be equal for 1M-1W teams
            
            # 2. Try many different pairings of the 'neediest' players
            for _ in range(iterations_per_round):
                # Strictly pick the players who need to play most
                selected_men = self._get_neediest_players(self.men, actual_needed_men)
                selected_women = self._get_neediest_players(self.women, actual_needed_women)
                
                actual_courts = len(selected_men) // 2
                
                random.shuffle(selected_men)
                random.shuffle(selected_women)
                
                current_matches = []
                for i in range(actual_courts):
                    current_matches.append([
                        [selected_men[2*i], selected_women[2*i]], 
                        [selected_men[2*i+1], selected_women[2*i+1]]
                    ])

                penalty = self._calculate_round_penalty(current_matches)
                if penalty < min_round_penalty:
                    min_round_penalty = penalty
                    best_round_matches = current_matches
                    if penalty == 0: break

            # Finalize the best round found
            final_matches = []
            for t1, t2 in best_round_matches:
                t1_tuple = tuple(t1)
                t2_tuple = tuple(t2)
                final_matches.append((t1_tuple, t2_tuple))
                
                for p in list(t1) + list(t2):
                    self.games_played[p] += 1
                self.teammate_counts[tuple(sorted(t1))] += 1
                self.teammate_counts[tuple(sorted(t2))] += 1
                for p1 in t1:
                    for p2 in t2:
                        self.opponent_counts[tuple(sorted((p1, p2)))] += 1
            
            self.schedule.append({
                "round": r,
                "matches": final_matches
            })
            
        return self.schedule


    def print_schedule(self):
        print(f"{'Round':<6} | {'Court':<6} | {'Team 1':<25} | {'Team 2':<25}")
        print("-" * 75)
        for round_data in self.schedule:
            r = round_data["round"]
            for i, match in enumerate(round_data["matches"]):
                t1, t2 = match
                t1_str = f"{t1[0]} & {t1[1]}"
                t2_str = f"{t2[0]} & {t2[1]}"
                print(f"{r:<6} | {i+1:<6} | {t1_str:<25} | {t2_str:<25}")
            print("-" * 75)

    def print_stats(self):
        print("\n--- Player Statistics ---")
        print(f"{'Player':<15} | {'Games Played':<12}")
        print("-" * 30)
        for p in sorted(self.games_played.keys()):
            print(f"{p:<15} | {self.games_played[p]:<12}")
            
        print("\n--- Repeat Teammates (Pairs) ---")
        teammate_repeats = {k: v for k, v in self.teammate_counts.items() if v > 1}
        if not teammate_repeats:
            print("None")
        else:
            for pair, count in sorted(teammate_repeats.items(), key=lambda x: x[1], reverse=True):
                print(f"{pair[0]} & {pair[1]}: {count} times")
            
        print("\n--- Repeat Opponents (Pairs) ---")
        opponent_repeats = {k: v for k, v in self.opponent_counts.items() if v > 1}
        if not opponent_repeats:
            print("None")
        else:
            # Sort by count then by names for clean output
            for pair, count in sorted(opponent_repeats.items(), key=lambda x: (x[1], x[0]), reverse=True):
                print(f"{pair[0]} vs {pair[1]}: {count} times")
    def ReturnHTMLSchedule(self) -> str:
        """
        Refactored to match the requested horizontal layout.
        Returns the schedule as a styled HTML table string.
        """
        headers = []
        rows = []
        
        if self.num_courts is None:
            headers = ["Game", "Team 1", "Team 2"]
            game_num = 1
            for round_data in self.schedule:
                for match in round_data["matches"]:
                    t1, t2 = match
                    rows.append([game_num, f"{t1[0]} & {t1[1]}", f"{t2[0]} & {t2[1]}"])
                    game_num += 1
        else:
            headers = ["Round"]
            for i in range(self.num_courts):
                headers.extend([f"Court {i+1} Team 1", f"Court {i+1} Team 2"])
            
            for round_data in self.schedule:
                row = [round_data["round"]]
                for match in round_data["matches"]:
                    t1, t2 = match
                    row.extend([f"{t1[0]} & {t1[1]}", f"{t2[0]} & {t2[1]}"])
                
                # Fill in empty courts if a round has fewer matches than courts
                while len(row) < len(headers):
                    row.extend(["-", "-"])
                rows.append(row)

        if headers and rows:
                return write_html_table(headers=headers, rows=rows, title="Tournament Schedule")
        # Inline implementation of write_html_table logic
        # html = [
        #     "<html><head><title>Tournament Schedule</title><style>",
        #     "table { border-collapse: collapse; width: 100%; font-family: sans-serif; margin-top: 20px; }",
        #     "th, td { border: 1px solid #ddd; padding: 12px; text-align: center; }",
        #     "th { background-color: #4CAF50; color: white; }",
        #     "tr:nth-child(even) { background-color: #f2f2f2; }",
        #     "tr:hover { background-color: #ddd; }",
        #     "h2 { font-family: sans-serif; color: #333; }",
        #     "</style></head><body>",
        #     "<h2>Tournament Schedule</h2>",
        #     "<table><thead><tr>"
        # ]
        # for h in headers:
        #     html.append(f"<th>{h}</th>")
        # html.append("</tr></thead><tbody>")
        
        # for r in rows:
        #     html.append("<tr>")
        #     for cell in r:
        #         html.append(f"<td>{cell}</td>")
        #     html.append("</tr>")
            
        # html.append("</tbody></table></body></html>")
        # return "\n".join(html)
        


if __name__ == "__main__":
    men_list = [f"M{i}" for i in range(1, 9)]
    women_list = [f"W{i}" for i in range(1, 9)]
    courts = 4
    rounds = 8
    
    scheduler = VolleyballScheduler(men_list, women_list, courts, rounds)
    scheduler.generate(iterations_per_round=15000) 
    scheduler.print_schedule()
    scheduler.print_stats()
    
    # Example of HTML output
    html_output = scheduler.get_html_table()
    with open("schedule.html", "w") as f:
        f.write(html_output)
    print("\nHTML schedule saved to 'schedule.html'")