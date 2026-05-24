from manus_scheduler2 import VolleyballScheduler

# men = ["Adam", "Bob", "Charlie", "David", "Edward", "Frank", "George", "Henry"]
# women = ["Alice", "Barb", "Chloe", "Diana", "Eve", "Fiona", "Grace", "Hannah"]
men = ["Adam", "Bob", "Charlie", "David", "Edward",]
women = ["Alice", "Barb", "Chloe", "Diana", "Eve", "Fiona", "Grace",]
courts = 2
rounds = 12

scheduler = VolleyballScheduler(men, women, courts, rounds)
schedule = scheduler.generate()
scheduler.print_schedule()
scheduler.print_stats()