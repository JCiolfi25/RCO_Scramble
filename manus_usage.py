from manus_scheduler2 import VolleyballScheduler

# men = ["Adam", "Bob", "Charlie", "David", "Edward", "Frank", "George", "Henry"]
# women = ["Alice", "Barb", "Chloe", "Diana", "Eve", "Fiona", "Grace", "Hannah"]
# men = ["Adam", "Bob", "Charlie", "David", "Edward",]
# women = ["Alice", "Barb", "Chloe", "Diana", "Eve", "Fiona", "Grace",]
men = ["Adam", "Bob", "Charlie", "David",]
women = ["Alice", "Barb", "Chloe", "Diane", "Eve"]
courts = 2
rounds = 10

scheduler = VolleyballScheduler(men, women, courts, rounds)
schedule = scheduler.generate()
scheduler.print_schedule()
scheduler.print_stats()