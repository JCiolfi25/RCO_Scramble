import random
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

    def _get_penalty(self, m1, w1, m2, w2) -> float:
        """
        Calculate the penalty for a specific match configuration.
        Match: (m1, w1) vs (m2, w2)
        """
        penalty = 0.0
        
        # Teammate repeats (M-W pairs)
        penalty += self.teammate_counts[tuple(sorted((m1, w1)))] * 100
        penalty += self.teammate_counts[tuple(sorted((m2, w2)))] * 100
        
        # Opponent repeats
        # Man vs Man
        penalty += self.opponent_counts[tuple(sorted((m1, m2)))] * 50
        # Woman vs Woman
        penalty += self.opponent_counts[tuple(sorted((w1, w2)))] * 50
        # Cross gender opponents
        penalty += self.opponent_counts[tuple(sorted((m1, w2)))] * 50
        penalty += self.opponent_counts[tuple(sorted((m2, w1)))] * 50
        
        # Balance games played
        # Higher penalty if players have already played more games than others
        avg_games = sum(self.games_played.values()) / len(self.games_played)
        for p in [m1, w1, m2, w2]:
            penalty += (self.games_played[p] - avg_games) * 10
            
        return penalty

    def generate(self):
        for r in range(1, self.num_rounds + 1):
            round_matches = []
            available_men = list(self.men)
            available_women = list(self.women)
            
            # Sort by games played to prioritize those who played less
            available_men.sort(key=lambda p: (self.games_played[p], random.random()))
            available_women.sort(key=lambda p: (self.games_played[p], random.random()))
            
            matches_this_round = 0
            while matches_this_round < self.num_courts and len(available_men) >= 2 and len(available_women) >= 2:
                best_match = None
                min_penalty = float('inf')
                
                # We try to find the best match from the most "needy" players
                # To keep it efficient but effective, we look at a subset of available players
                # or just pick the first few and find the best combination among them.
                
                # Strategy: Take the first 4 men and 4 women (most needy) and find best 4-tuple
                sample_m = available_men[:6]
                sample_w = available_women[:6]
                
                for i in range(len(sample_m)):
                    for j in range(i + 1, len(sample_m)):
                        for k in range(len(sample_w)):
                            for l in range(k + 1, len(sample_w)):
                                m1, m2 = sample_m[i], sample_m[j]
                                w1, w2 = sample_w[k], sample_w[l]
                                
                                # Try both pairing options: (m1, w1) vs (m2, w2) OR (m1, w2) vs (m2, w1)
                                # Option 1
                                p1 = self._get_penalty(m1, w1, m2, w2)
                                if p1 < min_penalty:
                                    min_penalty = p1
                                    best_match = ((m1, w1), (m2, w2))
                                
                                # Option 2
                                p2 = self._get_penalty(m1, w2, m2, w1)
                                if p2 < min_penalty:
                                    min_penalty = p2
                                    best_match = ((m1, w2), (m2, w1))
                
                if best_match:
                    t1, t2 = best_match
                    round_matches.append(best_match)
                    
                    # Update stats
                    for p in list(t1) + list(t2):
                        self.games_played[p] += 1
                    
                    self.teammate_counts[tuple(sorted(t1))] += 1
                    self.teammate_counts[tuple(sorted(t2))] += 1
                    
                    # Opponents
                    for p1 in t1:
                        for p2 in t2:
                            self.opponent_counts[tuple(sorted((p1, p2)))] += 1
                    
                    # Remove from available
                    available_men.remove(t1[0] if t1[0] in self.men else t1[1])
                    available_men.remove(t2[0] if t2[0] in self.men else t2[1])
                    available_women.remove(t1[1] if t1[1] in self.women else t1[0])
                    available_women.remove(t2[1] if t2[1] in self.women else t2[0])
                    
                    matches_this_round += 1
                else:
                    break
            
            self.schedule.append({
                "round": r,
                "matches": round_matches
            })
            
        return self.schedule

    def print_schedule(self):
        print(f"{'Round':<6} | {'Court':<6} | {'Team 1':<25} | {'Team 2':<25}")
        print("-" * 70)
        for round_data in self.schedule:
            r = round_data["round"]
            for i, match in enumerate(round_data["matches"]):
                t1, t2 = match
                t1_str = f"{t1[0]} & {t1[1]}"
                t2_str = f"{t2[0]} & {t2[1]}"
                print(f"{r:<6} | {i+1:<6} | {t1_str:<25} | {t2_str:<25}")
            print("-" * 70)

    def print_stats(self):
        print("\n--- Player Statistics ---")
        print(f"{'Player':<15} | {'Games Played':<12}")
        print("-" * 30)
        for p in sorted(self.games_played.keys()):
            print(f"{p:<15} | {self.games_played[p]:<12}")
            
        print("\n--- Repeat Teammates (Pairs) ---")
        repeats = {k: v for k, v in self.teammate_counts.items() if v > 1}
        if not repeats:
            print("None")
        for pair, count in repeats.items():
            print(f"{pair[0]} & {pair[1]}: {count} times")

if __name__ == "__main__":
    # Example usage
    men_list = ["Adam", "Bob", "Charlie", "David", "Edward", "Frank"]
    women_list = ["Alice", "Barb", "Chloe", "Diana", "Eve"]
    courts = 2
    rounds = 5
    
    scheduler = VolleyballScheduler(men_list, women_list, courts, rounds)
    scheduler.generate()
    scheduler.print_schedule()
    scheduler.print_stats()
