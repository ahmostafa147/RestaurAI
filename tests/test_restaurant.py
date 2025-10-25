import sys
sys.path.insert(0, '.')
from src.core.restaurant import Restaurant
from src.models.menu import MenuItem
from src.models.ingredient import Ingredient
from src.models.table import Table

def create_sample_menu():
    """Create a sample menu for testing"""
    return {
        "appetizers": [
            MenuItem(1, "Caesar Salad", 8.99, "appetizers", "Fresh romaine lettuce with parmesan and croutons", [Ingredient(1, "Romaine Lettuce", 1.0, "head")]),
            MenuItem(2, "Wings", 12.99, "appetizers", "Buffalo wings with your choice of sauce", [Ingredient(2, "Chicken", 1.0, "lbs")]),
        ],
        "entrees": [
            MenuItem(3, "Burger", 14.99, "entrees", "Classic beef burger with fries", [Ingredient(3, "Beef", 1.0, "lbs"), Ingredient(4, "Bread", 1.0, "slices"), Ingredient(5, "Cheese", 1.0, "slices"), Ingredient(6, "Lettuce", 1.0, "leaves"), Ingredient(7, "Tomato", 1.0, "slices"), Ingredient(8, "Onion", 1.0, "slices")]),
            MenuItem(4, "Steak", 24.99, "entrees", "Premium ribeye steak cooked to perfection", [Ingredient(9, "Ribeye Steak", 1.0, "lbs")]),
            MenuItem(5, "Pasta", 16.99, "entrees", "House-made pasta with marinara sauce", [Ingredient(10, "Pasta", 1.0, "lbs"), Ingredient(11, "Tomato Sauce", 1.0, "cups"), Ingredient(12, "Garlic", 1.0, "cloves"), Ingredient(13, "Basil", 1.0, "leaves")]),
        ],
        "desserts": [
            MenuItem(6, "Cheesecake", 7.99, "desserts", "New York style cheesecake", [Ingredient(6, "Cheesecake", 1.0, "lbs")]),
            MenuItem(7, "Ice Cream", 5.99, "desserts", "Vanilla, chocolate, or strawberry", [Ingredient(7, "Ice Cream", 1.0, "lbs")]),
        ]
    }

def create_sample_tables():
    """Create sample tables for testing"""
    return [
        Table(1, 2, "near window"),
        Table(2, 4, "center dining room"),
        Table(3, 6, "large family table"),
        Table(4, 2, "bar seat"),
        Table(5, 4, "outside patio"),
        Table(6, 2, "near window"),
        Table(7, 8, "private booth"),
        Table(8, 4, "center dining room")
    ]

def create_sample_inventory():
    """Create sample inventory for testing"""
    ingredients = [
        Ingredient(1, "Romaine Lettuce", 10.0, "head"),
        Ingredient(2, "Chicken", 25.0, "lbs"),
        Ingredient(3, "Beef", 15.0, "lbs"),
        Ingredient(4, "Bread", 50.0, "slices"),
        Ingredient(5, "Cheese", 20.0, "slices"),
        Ingredient(6, "Lettuce", 30.0, "leaves"),
        Ingredient(7, "Tomato", 25.0, "slices"),
        Ingredient(8, "Onion", 15.0, "slices"),
        Ingredient(9, "Ribeye Steak", 8.0, "lbs"),
        Ingredient(10, "Pasta", 12.0, "lbs"),
        Ingredient(11, "Tomato Sauce", 20.0, "cups"),
        Ingredient(12, "Garlic", 5.0, "cloves"),
        Ingredient(13, "Basil", 2.0, "leaves"),
        Ingredient(14, "Cheesecake", 3.0, "lbs"),
        Ingredient(15, "Ice Cream", 5.0, "lbs")
    ]
    # Convert to dictionary mapped by ingredient_id
    return {ingredient.id: ingredient for ingredient in ingredients}

# Create restaurant with sample menu, tables, and inventory
sample_menu = create_sample_menu()
sample_tables = create_sample_tables()
sample_inventory = create_sample_inventory()
r1 = Restaurant("Tony's Diner", menu=sample_menu, tables=sample_tables, inventory=sample_inventory)
print(f"Created: {r1.name}, Key: {r1.key}")

# Show available tables
print(f"Available tables: {r1.get_tables()}")

# Show available tables for party of 4
available_tables = r1.get_available_tables(4)
print(f"Tables for party of 4: {[table.to_dict() for table in available_tables]}")

# Show inventory
print(f"Inventory: {r1.get_inventory()}")

# Demonstrate dictionary benefits - direct access by ID
print(f"\n--- Dictionary Benefits ---")
beef = r1.get_ingredient(3)  # Direct O(1) lookup
print(f"Direct access to beef (ID 3): {beef.to_dict() if beef else 'Not found'}")

# Test ingredient checking
print("\n--- Testing Ingredient Availability ---")
# Check if we have enough beef for a burger
beef_needed = Ingredient(3, "Beef", 1.0, "lbs")
has_beef = r1.has_enough_ingredient(beef_needed)
print(f"Has enough beef for burger: {has_beef}")

# Check if we have enough of an ingredient we don't have much of
basil_needed = Ingredient(13, "Basil", 3.0, "leaves")  # Need 3, only have 2
has_basil = r1.has_enough_ingredient(basil_needed)
print(f"Has enough basil (need 3, have 2): {has_basil}")

# Check if we have enough of an ingredient we have plenty of
lettuce_needed = Ingredient(6, "Lettuce", 5.0, "leaves")  # Need 5, have 30
has_lettuce = r1.has_enough_ingredient(lettuce_needed)
print(f"Has enough lettuce (need 5, have 30): {has_lettuce}")

# Test adding ingredients
print(f"\n--- Testing Inventory Management ---")
print(f"Beef before adding: {r1.get_ingredient(3).quantity} lbs")
r1.add_ingredient(Ingredient(3, "Beef", 5.0, "lbs"))  # Add 5 more lbs
print(f"Beef after adding 5 lbs: {r1.get_ingredient(3).quantity} lbs")

# Test name-based lookups
print(f"\n--- Testing Name-Based Lookups ---")
# Lookup by name
beef_by_name = r1.get_ingredient_by_name("Beef")
print(f"Beef by name: {beef_by_name.to_dict() if beef_by_name else 'Not found'}")

# Test flexible lookup (ID or name)
beef_by_id = r1.get_ingredient_by_id_or_name(3)
beef_by_name_flex = r1.get_ingredient_by_id_or_name("Beef")
print(f"Beef by ID (flexible): {beef_by_id.to_dict() if beef_by_id else 'Not found'}")
print(f"Beef by name (flexible): {beef_by_name_flex.to_dict() if beef_by_name_flex else 'Not found'}")

# Test removing by name
print(f"Chicken before removing: {r1.get_ingredient_by_name('Chicken').quantity} lbs")
r1.remove_ingredient_by_name("Chicken", 5.0)  # Remove 5 lbs by name
print(f"Chicken after removing 5 lbs: {r1.get_ingredient_by_name('Chicken').quantity} lbs")

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

# Create another restaurant (without menu, tables, or inventory)
r3 = Restaurant("Maria's Bistro")
print(f"\nCreated: {r3.name}, Key: {r3.key}")
print(f"R3 Tables: {r3.get_tables()}")  # Should be empty
print(f"R3 Inventory: {r3.get_inventory()}")  # Should be empty
r3.reserve_table("Alice", 2, "8:00 PM")
print(f"R3 Reservations: {r3.get_reservations()}")
print(f"R1 Reservations: {r1.get_reservations()}")
