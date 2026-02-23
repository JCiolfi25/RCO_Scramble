def generate_full_round(men, women, round_idx):
    """
    Generate the full set of teams for a round (no court limits yet).
    Uses deterministic partner rotation.
    """
    n = len(men)

    # Rotate women to create unique partners
    rotated_women = women[round_idx%n:] + women[:round_idx%n]

    teams = list(zip(men, rotated_women))

    # Rotate matchup structure to vary opponents
    offset = round_idx % (n - 1) if n > 2 else 0
    reordered = teams[:1] + teams[1+offset:] + teams[1:1+offset]

    # Pair teams into matches
    matches = []
    for i in range(0, n, 2):
        matches.append((reordered[i], reordered[i+1]))

    return matches


def select_matches_with_court_limit(matches, courts, round_idx):
    """
    Deterministically choose which matches are played this round.
    Rotates selection so byes are evenly distributed.
    """
    total_matches = len(matches)

    if courts >= total_matches:
        return matches  # everyone plays

    start = (round_idx * courts) % total_matches

    selected = []
    for i in range(courts):
        idx = (start + i) % total_matches
        selected.append(matches[idx])

    return selected


def generate_schedule(num_men, num_women, courts, rounds):
    if num_men != num_women:
        raise ValueError("This deterministic model requires equal men and women.")

    if num_men % 2 != 0:
        raise ValueError("Use an even number of each gender.")

    men = [f"M{i+1}" for i in range(num_men)]
    women = [f"W{i+1}" for i in range(num_women)]

    schedule = []

    for r in range(rounds):
        full_round = generate_full_round(men, women, r)
        played_matches = select_matches_with_court_limit(full_round, courts, r)
        schedule.append(played_matches)

    return schedule


def print_schedule(schedule):
    for r, matches in enumerate(schedule, 1):
        print(f"\n=== ROUND {r} ===")
        for c, match in enumerate(matches, 1):
            (m1, w1), (m2, w2) = match
            print(f"Court {c}: {m1}/{w1} vs {m2}/{w2}")

import csv

def export_schedule_to_csv(schedule, filename="tournament_schedule.csv", matches_only=False):
    """
    Export schedule with ONE ROW PER ROUND.
    Each court gets its own set of columns.
    """

    if not schedule:
        print("No schedule to export.")
        return

    max_courts = max(len(round_matches) for round_matches in schedule)

    if not matches_only:
        # Build header dynamically based on number of courts
        header = ["Round"]
        for c in range(1, max_courts + 1):
            header.extend([
                f"Court{c}_TeamA_P1",
                f"Court{c}_TeamA_P2",
                f"Court{c}_TeamB_P1",
                f"Court{c}_TeamB_P2",
            ])

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)

        if not matches_only: 
            writer.writerow(header)

        for round_number, matches in enumerate(schedule, start=1):
            row = list()

            for match in matches:
                (a1, a2), (b1, b2) = match
                row.extend([a1, a2, b1, b2])
                if matches_only:
                    #If only printing matches, write each match as its own row immediately
                    writer.writerow(row)
                    row = list()

            if not matches_only:
                # If not only printing matches and this round used fewer courts than the maximum, pad blanks
                missing = max_courts - len(matches)
                for _ in range(missing):
                    row.extend(["", "", "", ""])
                writer.writerow(row)   

    print(f"Schedule exported to {filename}")

if __name__ == "__main__":
    num_players = int(input("Enter number of men (same as women): "))
    courts = int(input("Enter number of available courts: "))
    rounds = int(input("Enter number of rounds to schedule: "))

    schedule = generate_schedule(num_players, num_players, courts, rounds)
    export_schedule_to_csv(schedule, matches_only=True)
    print_schedule(schedule)