import sys
sys.path.insert(0, '.')
from src.core.restaurant import Restaurant

# Create restaurant
r1 = Restaurant("Tony's Diner")
print(f"Created: {r1.name}, Key: {r1.key}")

# Make reservation
res = r1.reserve_table("John", 4, "7:00 PM")
print(f"Reservation: {res}")

# Place order
order = r1.place_order(1, [1, 3, 6])
print(f"Order: {order}")

# Load same restaurant with key
r2 = Restaurant(key=r1.key)
print(f"\nLoaded restaurant: {r2.name}")
print(f"Reservations: {r2.get_reservations()}")
print(f"Orders: {r2.get_orders()}")

# Create another restaurant
r3 = Restaurant("Maria's Bistro")
print(f"\nCreated: {r3.name}, Key: {r3.key}")
r3.reserve_table("Alice", 2, "8:00 PM")
print(f"R3 Reservations: {r3.get_reservations()}")
print(f"R1 Reservations: {r1.get_reservations()}")
