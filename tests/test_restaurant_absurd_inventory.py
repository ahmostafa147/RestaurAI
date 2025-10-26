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
            MenuItem(1, "Caesar Salad", 8.99, "appetizers", "Fresh romaine lettuce with parmesan and croutons", True, [Ingredient(1, "Romaine Lettuce", 1.0, "head")]),
            MenuItem(2, "Wings", 12.99, "appetizers", "Buffalo wings with your choice of sauce", True, [Ingredient(2, "Chicken", 1.0, "lbs")]),
        ],
        "entrees": [
            MenuItem(3, "Burger", 14.99, "entrees", "Classic beef burger with fries", True, [Ingredient(3, "Beef", 1.0, "lbs"), Ingredient(4, "Bread", 1.0, "slices"), Ingredient(5, "Cheese", 1.0, "slices"), Ingredient(6, "Lettuce", 1.0, "leaves"), Ingredient(7, "Tomato", 1.0, "slices"), Ingredient(8, "Onion", 1.0, "slices")]),
            MenuItem(4, "Steak", 24.99, "entrees", "Premium ribeye steak cooked to perfection", True, [Ingredient(9, "Ribeye Steak", 1.0, "lbs")]),
            MenuItem(5, "Pasta", 16.99, "entrees", "House-made pasta with marinara sauce", True, [Ingredient(10, "Pasta", 1.0, "lbs"), Ingredient(11, "Tomato Sauce", 1.0, "cups"), Ingredient(12, "Garlic", 1.0, "cloves"), Ingredient(13, "Basil", 1.0, "leaves")]),
        ],
        "desserts": [
            MenuItem(6, "Cheesecake", 7.99, "desserts", "New York style cheesecake", True, [Ingredient(14, "Cheesecake", 1.0, "lbs")]),
            MenuItem(7, "Ice Cream", 5.99, "desserts", "Vanilla, chocolate, or strawberry", True, [Ingredient(15, "Ice Cream", 1.0, "lbs")]),
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

def create_absurd_inventory():
    """Create absurd inventory with major issues for ingredient agent testing"""
    ingredients = [
        # CRITICALLY LOW INVENTORY - These will cause menu items to be unavailable
        Ingredient(1, "Romaine Lettuce", 0.1, "head"),  # Need 1.0, only have 0.1 - CRITICAL
        Ingredient(2, "Chicken", 0.05, "lbs"),  # Need 1.0, only have 0.05 - CRITICAL
        Ingredient(3, "Beef", 0.2, "lbs"),  # Need 1.0, only have 0.2 - CRITICAL
        
        # EXCESSIVE INVENTORY - Way too much of these ingredients
        Ingredient(4, "Bread", 5000.0, "slices"),  # Need 1.0, have 5000 - EXCESSIVE
        Ingredient(5, "Cheese", 10000.0, "slices"),  # Need 1.0, have 10000 - EXCESSIVE
        Ingredient(6, "Lettuce", 2000.0, "leaves"),  # Need 1.0, have 2000 - EXCESSIVE
        
        # MODERATE ISSUES
        Ingredient(7, "Tomato", 0.3, "slices"),  # Need 1.0, only have 0.3 - LOW
        Ingredient(8, "Onion", 0.1, "slices"),  # Need 1.0, only have 0.1 - CRITICAL
        Ingredient(9, "Ribeye Steak", 0.05, "lbs"),  # Need 1.0, only have 0.05 - CRITICAL
        Ingredient(10, "Pasta", 0.2, "lbs"),  # Need 1.0, only have 0.2 - CRITICAL
        Ingredient(11, "Tomato Sauce", 0.1, "cups"),  # Need 1.0, only have 0.1 - CRITICAL
        Ingredient(12, "Garlic", 0.05, "cloves"),  # Need 1.0, only have 0.05 - CRITICAL
        Ingredient(13, "Basil", 0.02, "leaves"),  # Need 1.0, only have 0.02 - CRITICAL
        Ingredient(14, "Cheesecake", 0.1, "lbs"),  # Need 1.0, only have 0.1 - CRITICAL
        Ingredient(15, "Ice Cream", 0.05, "lbs"),  # Need 1.0, only have 0.05 - CRITICAL
        
        # COMPLETELY UNUSED INGREDIENTS - Not used in any recipes
        Ingredient(16, "Truffle Oil", 50.0, "oz"),  # Expensive, unused
        Ingredient(17, "Caviar", 10.0, "oz"),  # Very expensive, unused
        Ingredient(18, "Wagyu Beef", 5.0, "lbs"),  # Extremely expensive, unused
        Ingredient(19, "Gold Leaf", 100.0, "sheets"),  # Decorative, unused
        Ingredient(20, "Saffron", 2.0, "oz"),  # Very expensive spice, unused
        Ingredient(21, "Lobster", 20.0, "lbs"),  # Expensive seafood, unused
        Ingredient(22, "Foie Gras", 3.0, "lbs"),  # Expensive delicacy, unused
        Ingredient(23, "Kobe Beef", 2.0, "lbs"),  # Extremely expensive, unused
        Ingredient(24, "White Truffle", 1.0, "oz"),  # Most expensive, unused
        Ingredient(25, "Beluga Caviar", 0.5, "oz"),  # Most expensive caviar, unused
        
        # EXPIRED/SPOILED INGREDIENTS (simulated with negative availability)
        Ingredient(26, "Expired Milk", 10.0, "gallons", False),  # Expired
        Ingredient(27, "Spoiled Fish", 5.0, "lbs", False),  # Spoiled
        Ingredient(28, "Rotten Vegetables", 15.0, "lbs", False),  # Rotten
        
        # INGREDIENTS WITH WRONG UNITS (potential confusion)
        Ingredient(29, "Salt", 1000.0, "tons"),  # Way too much salt
        Ingredient(30, "Pepper", 500.0, "pounds"),  # Way too much pepper
    ]
    # Convert to dictionary mapped by ingredient_id
    return {ingredient.id: ingredient for ingredient in ingredients}

# Create restaurant with absurd inventory issues
sample_menu = create_sample_menu()
sample_tables = create_sample_tables()
absurd_inventory = create_absurd_inventory()
r1 = Restaurant("Chaos Kitchen", menu=sample_menu, tables=sample_tables, inventory=absurd_inventory)
print(f"Created: {r1.name}, Key: {r1.key}")

print(f"\n=== CHAOS KITCHEN - ABSURD INVENTORY TEST ===")
print(f"Restaurant Key: {r1.key}")
print(f"This restaurant has been created with intentionally problematic inventory:")
print(f"- Critically low inventory on essential ingredients")
print(f"- Excessive inventory on some ingredients") 
print(f"- Completely unused expensive ingredients")
print(f"- Expired/spoiled ingredients")
print(f"- Ingredients with wrong units")

# Show the problematic inventory
print(f"\n--- INVENTORY ANALYSIS ---")
inventory = r1.get_inventory()
print(f"Total inventory items: {len(inventory)}")

# Categorize inventory issues
critical_low = []
excessive = []
unused = []
expired = []
wrong_units = []

for item in inventory:
    if not item.get('available', True):
        expired.append(item)
    elif item['quantity'] < 1.0 and item['id'] <= 15:  # Menu ingredients with low stock
        critical_low.append(item)
    elif item['quantity'] > 1000.0:  # Excessive inventory
        excessive.append(item)
    elif item['id'] > 15 and item['id'] <= 25:  # Unused expensive ingredients
        unused.append(item)
    elif item['id'] > 25:  # Wrong units or expired
        if item['id'] <= 28:
            expired.append(item)
        else:
            wrong_units.append(item)

print(f"\nCRITICAL LOW INVENTORY ({len(critical_low)} items):")
for item in critical_low:
    print(f"  - {item['name']}: {item['quantity']} {item['unit']} (CRITICAL)")

print(f"\nEXCESSIVE INVENTORY ({len(excessive)} items):")
for item in excessive:
    print(f"  - {item['name']}: {item['quantity']} {item['unit']} (EXCESSIVE)")

print(f"\nUNUSED EXPENSIVE INGREDIENTS ({len(unused)} items):")
for item in unused:
    print(f"  - {item['name']}: {item['quantity']} {item['unit']} (UNUSED)")

print(f"\nEXPIRED/SPOILED INGREDIENTS ({len(expired)} items):")
for item in expired:
    print(f"  - {item['name']}: {item['quantity']} {item['unit']} (EXPIRED/SPOILED)")

print(f"\nWRONG UNITS ({len(wrong_units)} items):")
for item in wrong_units:
    print(f"  - {item['name']}: {item['quantity']} {item['unit']} (WRONG UNITS)")

# Test menu availability with these issues
print(f"\n--- MENU AVAILABILITY ANALYSIS ---")
menu = r1.get_menu_dict()
unavailable_items = []
available_items = []

for category, items in menu.items():
    for item in items:
        if item.get('available', True):
            available_items.append(item['name'])
        else:
            unavailable_items.append(item['name'])

print(f"Available menu items ({len(available_items)}): {available_items}")
print(f"Unavailable menu items ({len(unavailable_items)}): {unavailable_items}")

# Test some orders to see the chaos
print(f"\n--- ORDER CHAOS TEST ---")
ticket = r1.create_ticket(1)
print(f"Created ticket: {ticket}")

# Try to order items that should fail due to low inventory
print(f"\nTrying to order Caesar Salad (needs Romaine Lettuce - only 0.1 available):")
order1 = r1.place_order(1, 1, ticket["id"])  # Caesar Salad
print(f"Order 1: {order1}")

print(f"\nTrying to order Wings (needs Chicken - only 0.05 available):")
order2 = r1.place_order(1, 2, ticket["id"])  # Wings  
print(f"Order 2: {order2}")

print(f"\nTrying to order Burger (needs Beef - only 0.2 available):")
order3 = r1.place_order(1, 3, ticket["id"])  # Burger
print(f"Order 3: {order3}")

print(f"\nTrying to order Steak (needs Ribeye Steak - only 0.05 available):")
order4 = r1.place_order(1, 4, ticket["id"])  # Steak
print(f"Order 4: {order4}")

print(f"\nTrying to order Pasta (needs multiple ingredients with low stock):")
order5 = r1.place_order(1, 5, ticket["id"])  # Pasta
print(f"Order 5: {order5}")

print(f"\nTrying to order Cheesecake (needs Cheesecake - only 0.1 available):")
order6 = r1.place_order(1, 6, ticket["id"])  # Cheesecake
print(f"Order 6: {order6}")

print(f"\nTrying to order Ice Cream (needs Ice Cream - only 0.05 available):")
order7 = r1.place_order(1, 7, ticket["id"])  # Ice Cream
print(f"Order 7: {order7}")

# Show final ticket state
ticket_details = r1.get_ticket(ticket["id"])
print(f"\nFinal ticket details: {ticket_details}")
print(f"Total orders in ticket: {len(ticket_details.get('orders', []))}")
print(f"Ticket total: ${ticket_details.get('total', 0)}")

# Calculate waste and inefficiency
print(f"\n--- INVENTORY WASTE ANALYSIS ---")
total_inventory_value = 0
wasted_inventory_value = 0

# Estimate costs (simplified)
cost_estimates = {
    "Bread": 0.10, "Cheese": 0.25, "Lettuce": 0.05,  # Excessive items
    "Truffle Oil": 50.0, "Caviar": 200.0, "Wagyu Beef": 100.0,  # Unused expensive
    "Gold Leaf": 5.0, "Saffron": 500.0, "Lobster": 30.0,  # More unused expensive
    "Foie Gras": 80.0, "Kobe Beef": 200.0, "White Truffle": 1000.0,  # Most expensive
    "Beluga Caviar": 500.0  # Most expensive caviar
}

for item in inventory:
    cost_per_unit = cost_estimates.get(item['name'], 1.0)  # Default $1 per unit
    item_value = item['quantity'] * cost_per_unit
    total_inventory_value += item_value
    
    # Count as waste if excessive, unused, or expired
    if (item['quantity'] > 1000.0 or 
        (item['id'] > 15 and item['id'] <= 25) or 
        not item.get('available', True)):
        wasted_inventory_value += item_value

print(f"Total inventory value: ${total_inventory_value:,.2f}")
print(f"Wasted inventory value: ${wasted_inventory_value:,.2f}")
print(f"Waste percentage: {(wasted_inventory_value/total_inventory_value)*100:.1f}%")

print(f"\n=== RESTAURANT SAVED FOR INGREDIENT AGENT TESTING ===")
print(f"Restaurant Key: {r1.key}")
print(f"Use this key to test the ingredient agent's analytics capabilities!")
print(f"The ingredient agent should identify:")
print(f"  - Critical inventory shortages")
print(f"  - Excessive inventory waste") 
print(f"  - Unused expensive ingredients")
print(f"  - Expired/spoiled items")
print(f"  - Unit conversion issues")
