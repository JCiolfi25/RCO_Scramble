import random
import copy
from collections import defaultdict
from typing import List, Dict, Tuple, Set

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
        """
        Calculate total penalty for a potential round configuration.
        Matches are expected as a list of [team1, team2] where each team is [man, woman].
        """
        penalty = 0.0
        
        for t1, t2 in round_matches:
            # Teammate repeats (M-W pairs)
            # Use a very high penalty for repeat teammates
            penalty += self.teammate_counts[tuple(sorted(t1))] * 10000
            penalty += self.teammate_counts[tuple(sorted(t2))] * 10000
            
            # Opponent repeats
            for p1 in t1:
                for p2 in t2:
                    penalty += self.opponent_counts[tuple(sorted((p1, p2)))] * 100
        
        return penalty

    def generate(self, iterations_per_round: int = 10000):
        for r in range(1, self.num_rounds + 1):
            # 1. Select players for this round based on games played
            pool_men = sorted(self.men, key=lambda p: (self.games_played[p], random.random()))
            pool_women = sorted(self.women, key=lambda p: (self.games_played[p], random.random()))
            
            needed = 2 * self.num_courts
            selected_men = pool_men[:needed]
            selected_women = pool_women[:needed]
            
            actual_courts = min(self.num_courts, len(selected_men) // 2, len(selected_women) // 2)
            selected_men = selected_men[:actual_courts*2]
            selected_women = selected_women[:actual_courts*2]

            # 2. Start with a random initial configuration
            random.shuffle(selected_men)
            random.shuffle(selected_women)
            
            # current_matches is a list of [team1, team2] where each team is [man, woman]
            best_round_matches = []
            for i in range(actual_courts):
                best_round_matches.append([
                    [selected_men[2*i], selected_women[2*i]], 
                    [selected_men[2*i+1], selected_women[2*i+1]]
                ])

            min_round_penalty = self._calculate_round_penalty(best_round_matches)

            # 3. Hill Climbing Optimization
            for _ in range(iterations_per_round):
                if min_round_penalty == 0:
                    break
                
                # Try a random modification on a deep copy
                new_matches = copy.deepcopy(best_round_matches)
                mod_type = random.choice(["swap_women", "swap_men", "swap_teams"])
                
                if mod_type == "swap_women":
                    # Swap women between two random teams
                    c1, c2 = random.sample(range(actual_courts), 2)
                    s1, s2 = random.randint(0, 1), random.randint(0, 1)
                    new_matches[c1][s1][1], new_matches[c2][s2][1] = \
                        new_matches[c2][s2][1], new_matches[c1][s1][1]
                
                elif mod_type == "swap_men":
                    # Swap men between two random teams
                    c1, c2 = random.sample(range(actual_courts), 2)
                    s1, s2 = random.randint(0, 1), random.randint(0, 1)
                    new_matches[c1][s1][0], new_matches[c2][s2][0] = \
                        new_matches[c2][s2][0], new_matches[c1][s1][0]
                
                elif mod_type == "swap_teams":
                    # Swap entire teams between courts
                    if actual_courts > 1:
                        c1, c2 = random.sample(range(actual_courts), 2)
                        s1, s2 = random.randint(0, 1), random.randint(0, 1)
                        new_matches[c1][s1], new_matches[c2][s2] = \
                            new_matches[c2][s2], new_matches[c1][s1]

                new_penalty = self._calculate_round_penalty(new_matches)
                if new_penalty <= min_round_penalty:
                    min_round_penalty = new_penalty
                    best_round_matches = new_matches

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

if __name__ == "__main__":
    men_list = [f"M{i}" for i in range(1, 9)]
    women_list = [f"W{i}" for i in range(1, 9)]
    courts = 4
    rounds = 8
    
    scheduler = VolleyballScheduler(men_list, women_list, courts, rounds)
    scheduler.generate(iterations_per_round=15000) 
    scheduler.print_schedule()
    scheduler.print_stats()