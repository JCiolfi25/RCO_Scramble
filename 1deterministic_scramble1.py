def generate_schedule(n):
    """
    Deterministic rotating-partner schedule.
    Requires equal number of men and women.
    Produces n rounds with no repeated partners.
    """

    men = [f"M{i+1}" for i in range(n)]
    women = [f"W{i+1}" for i in range(n)]

    schedule = []

    for round_idx in range(n):
        # --- Rotate women list deterministically ---
        rotated_women = women[round_idx:] + women[:round_idx]

        # Create teams (unique partners every round)
        teams = list(zip(men, rotated_women))

        # --- Rotate match pairings to balance opponents ---
        # This prevents repeating the same adjacent matchups
        offset = round_idx % (n - 1) if n > 2 else 0
        reordered = teams[:1] + teams[1+offset:] + teams[1:1+offset]

        # Pair teams into matches
        matches = []
        for i in range(0, n, 2):
            team1 = reordered[i]
            team2 = reordered[i+1]
            matches.append((team1, team2))

        schedule.append(matches)

    return schedule


def print_schedule(schedule):
    for r, matches in enumerate(schedule, 1):
        print(f"\n=== ROUND {r} ===")
        for c, match in enumerate(matches, 1):
            (m1, w1), (m2, w2) = match
            print(f"Court {c}: {m1}/{w1}  vs  {m2}/{w2}")


if __name__ == "__main__":
    n = int(input("Enter number of men (must equal number of women): "))

    if n % 2 != 0:
        raise ValueError("Use an even number so everyone plays each round.")

    schedule = generate_schedule(n)
    print_schedule(schedule)