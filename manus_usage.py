from manus_scheduler2 import VolleyballScheduler

men = ["Adam", "Bob", "Charlie", "David", "Edward", "Frank", "George", "Henry"]
women = ["Alice", "Barb", "Chloe", "Diana", "Eve", "Fiona", "Grace", "Hannah"]
# men = ["Adam", "Bob", "Charlie", "David", "Edward",]
# women = ["Alice", "Barb", "Chloe", "Diana", "Eve", "Fiona", "Grace",]
# men = ["Adam", "Bob", "Charlie"]
# women = ["Alice", "Barb", "Chloe",]
courts = 4
rounds = 8

scheduler = VolleyballScheduler(men, women, courts, rounds)
schedule = scheduler.generate()
scheduler.print_schedule()
scheduler.print_stats()