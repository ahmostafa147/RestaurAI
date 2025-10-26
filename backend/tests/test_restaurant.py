import sys
sys.path.insert(0, '.')
from backend.src.core.restaurant import Restaurant
from backend.src.models.menu import MenuItem
from backend.src.models.ingredient import Ingredient
from backend.src.models.table import Table

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

# Show inventory
print(f"Menu: {r1.get_menu_dict()}")
# Show inventory
print(f"Inventory: {r1.get_inventory()}")

# Demonstrate dictionary benefits - direct access by ID
print(f"\n--- Dictionary Benefits ---")
beef = r1.get_ingredient(3)  # Direct O(1) lookup
print(f"Direct access to beef (ID 3): {beef.to_dict() if beef else 'Not found'}")
assert beef is not None, "Beef ingredient should exist"
assert beef.name == "Beef", "Beef ingredient should have correct name"
assert beef.quantity == 15.0, "Beef should have 15.0 lbs initially"

# Test ingredient checking
print("\n--- Testing Ingredient Availability ---")
# Check if we have enough beef for a burger
beef_needed = Ingredient(3, "Beef", 1.0, "lbs")
has_beef = r1.has_enough_ingredient(beef_needed)
print(f"Has enough beef for burger: {has_beef}")
assert has_beef == True, "Should have enough beef for burger"

# Check if we have enough of an ingredient we don't have much of
basil_needed = Ingredient(13, "Basil", 3.0, "leaves")  # Need 3, only have 2
has_basil = r1.has_enough_ingredient(basil_needed)
print(f"Has enough basil (need 3, have 2): {has_basil}")
assert has_basil == False, "Should not have enough basil (need 3, have 2)"

# Check if we have enough of an ingredient we have plenty of
lettuce_needed = Ingredient(6, "Lettuce", 5.0, "leaves")  # Need 5, have 30
has_lettuce = r1.has_enough_ingredient(lettuce_needed)
print(f"Has enough lettuce (need 5, have 30): {has_lettuce}")
assert has_lettuce == True, "Should have enough lettuce (need 5, have 30)"

# Test adding ingredients
print(f"\n--- Testing Inventory Management ---")
beef_before = r1.get_ingredient(3).quantity
print(f"Beef before adding: {beef_before} lbs")
r1.add_ingredient(Ingredient(3, "Beef", 5.0, "lbs"))  # Add 5 more lbs
beef_after = r1.get_ingredient(3).quantity
print(f"Beef after adding 5 lbs: {beef_after} lbs")
assert beef_after == beef_before + 5.0, f"Beef should increase by 5 lbs (was {beef_before}, now {beef_after})"

# Test name-based lookups
print(f"\n--- Testing Name-Based Lookups ---")
# Lookup by name
beef_by_name = r1.get_ingredient_by_name("Beef")
print(f"Beef by name: {beef_by_name.to_dict() if beef_by_name else 'Not found'}")
assert beef_by_name is not None, "Beef should be found by name"
assert beef_by_name.id == 3, "Beef by name should have correct ID"

# Test flexible lookup (ID or name)
beef_by_id = r1.get_ingredient_by_id_or_name(3)
beef_by_name_flex = r1.get_ingredient_by_id_or_name("Beef")
print(f"Beef by ID (flexible): {beef_by_id.to_dict() if beef_by_id else 'Not found'}")
print(f"Beef by name (flexible): {beef_by_name_flex.to_dict() if beef_by_name_flex else 'Not found'}")
assert beef_by_id is not None, "Beef should be found by ID"
assert beef_by_name_flex is not None, "Beef should be found by name"
assert beef_by_id.id == beef_by_name_flex.id, "Both lookups should return same ingredient"

# Test removing by name
chicken_before = r1.get_ingredient_by_name('Chicken').quantity
print(f"Chicken before removing: {chicken_before} lbs")
r1.remove_ingredient_by_name("Chicken", 5.0)  # Remove 5 lbs by name
chicken_after = r1.get_ingredient_by_name('Chicken').quantity
print(f"Chicken after removing 5 lbs: {chicken_after} lbs")
assert chicken_after == chicken_before - 5.0, f"Chicken should decrease by 5 lbs (was {chicken_before}, now {chicken_after})"

# Create ticket and place orders
ticket = r1.create_ticket(1)
print(f"Created ticket: {ticket}")
assert ticket["id"] == 1, "First ticket should have ID 1"
assert ticket["table"] == 1, "Ticket should be for table 1"
assert ticket["status"] == "open", "Ticket should be open initially"
assert ticket["total"] == 0.0, "Ticket should start with 0 total"

# Place individual orders
order1 = r1.place_order(1, 1, ticket["id"])  # Caesar Salad
print(f"Order 1: {order1}")
assert order1["status"] == "pending", "Order should be pending"
assert order1["total"] == 8.99, "Caesar Salad should cost $8.99"

order2 = r1.place_order(1, 3, ticket["id"])  # Burger
print(f"Order 2: {order2}")
assert order2["status"] == "pending", "Order should be pending"
assert order2["total"] == 14.99, "Burger should cost $14.99"

order3 = r1.place_order(1, 6, ticket["id"])  # Cheesecake
print(f"Order 3: {order3}")
assert order3["status"] == "pending", "Order should be pending"
assert order3["total"] == 7.99, "Cheesecake should cost $7.99"

# Show ticket details
ticket_details = r1.get_ticket(ticket["id"])
print(f"Ticket details: {ticket_details}")
assert len(ticket_details["orders"]) == 3, "Ticket should have 3 orders"
assert ticket_details["total"] == 8.99 + 14.99 + 7.99, "Ticket total should be sum of orders"

# Show all active tickets
active_tickets = r1.get_tickets()
print(f"Active tickets: {active_tickets}")
assert len(active_tickets) == 1, "Should have 1 active ticket"

# Close the ticket
closed = r1.close_ticket(ticket["id"])
print(f"Ticket closed: {closed}")
assert closed == True, "Ticket should close successfully"

# Show tickets after closing
active_tickets_after = r1.get_tickets()
print(f"Active tickets after closing: {active_tickets_after}")
assert len(active_tickets_after) == 0, "Should have no active tickets after closing"


# Load same restaurant with key
r2 = Restaurant(key=r1.key)
print(f"\nLoaded restaurant: {r2.name}")
print(f"Active tickets: {r2.get_tickets()}")
print(f"All orders: {r2.get_orders()}")
assert r2.name == r1.name, "Loaded restaurant should have same name"
assert len(r2.get_tickets()) == 0, "Should have no active tickets after restart"

# Test persistent inventory
print(f"\n--- Testing Persistent Inventory ---")
beef_quantity = r2.get_ingredient(3).quantity
chicken_quantity = r2.get_ingredient_by_name('Chicken').quantity
print(f"Beef quantity after restart: {beef_quantity} lbs")
print(f"Chicken quantity after restart: {chicken_quantity} lbs")
assert beef_quantity == 19.0, f"Beef should be 19.0 lbs after restart (was {beef_quantity}) - started at 15.0, added 5.0, consumed 1.0 by burger order"
assert chicken_quantity == 20.0, f"Chicken should be 20.0 lbs after restart (was {chicken_quantity})"

# Test ticket counter persistence
print(f"\n--- Testing Ticket Counter Persistence ---")
new_ticket = r2.create_ticket(2)
print(f"New ticket ID after restart: {new_ticket['id']}")  # Should be next in sequence
assert new_ticket["id"] == 2, "New ticket should have ID 2 (continuing from previous)"

# Create another restaurant (without menu, tables, or inventory)
r3 = Restaurant("Maria's Bistro")
print(f"\nCreated: {r3.name}, Key: {r3.key}")
print(f"R3 Inventory: {r3.get_inventory()}")  # Should be empty
print(f"R3 Active tickets: {r3.get_tickets()}")  # Should be empty
assert r3.name == "Maria's Bistro", "New restaurant should have correct name"
assert len(r3.get_inventory()) == 0, "New restaurant should have empty inventory"
assert len(r3.get_tickets()) == 0, "New restaurant should have no active tickets"

# Test ingredient availability and menu updates
print(f"\n--- Testing Menu Availability ---")
print(f"Menu before orders: {r1.get_menu()}")

# Test insufficient ingredients scenario
print(f"\n--- Testing Insufficient Ingredients ---")
# Try to place an order that requires more ingredients than available
basil_ingredient = r1.get_ingredient_by_name("Basil")
print(f"Current basil quantity: {basil_ingredient.quantity}")

# Create a menu item that needs more basil than we have
from backend.src.models.menu import MenuItem
from backend.src.models.ingredient import Ingredient
test_item = MenuItem(
    id=99, 
    name="Test Pasta", 
    price=20.0, 
    category="entrees", 
    description="Test item needing lots of basil", 
    ingredients=[Ingredient(12, "Basil", 10.0, "leaves")]
)  # Need 10, only have 2
print(f"Created test item with ingredients: {test_item.ingredients}")
added = r1.order_manager.add_menu_item(test_item)
print(f"Added test item: {added}")

# Verify the test item was added and has the correct ingredients
added_item = r1.order_manager.get_menu_item(99)
print(f"Retrieved test item: {added_item}")
if added_item:
    print(f"Test item ingredients: {added_item.ingredients}")
    print(f"Number of ingredients: {len(added_item.ingredients)}")
    if len(added_item.ingredients) > 0:
        print(f"First ingredient: {added_item.ingredients[0]}")

# Try to place order for test item
test_ticket = r1.create_ticket(3)
test_order = r1.place_order(3, 99, test_ticket["id"])
print(f"Order for insufficient ingredients: {test_order}")
assert test_order["status"] == "rejected", "Order should be rejected due to insufficient ingredients"
assert "Insufficient ingredients" in test_order["reason"], "Rejection reason should mention insufficient ingredients"

# Show updated menu availability
print(f"Menu after testing: {r1.get_menu()}")

# Test multiple tickets and orders
print(f"\n--- Testing Multiple Tickets ---")
ticket2 = r1.create_ticket(4)
print(f"Created second ticket: {ticket2}")
assert ticket2["id"] == 3, "Second ticket should have ID 3"
assert ticket2["table"] == 4, "Second ticket should be for table 4"

# Place orders on second ticket
order4 = r1.place_order(4, 2, ticket2["id"])  # Wings
order5 = r1.place_order(4, 4, ticket2["id"])  # Steak
print(f"Order 4: {order4}")
print(f"Order 5: {order5}")
assert order4["status"] == "pending", "Order 4 should be pending"
assert order5["status"] == "pending", "Order 5 should be pending"

# Show both tickets
all_tickets = r1.get_tickets()
print(f"All active tickets: {all_tickets}")
assert len(all_tickets) == 2, "Should have 2 active tickets (test ticket and ticket2)"

# Close second ticket
r1.close_ticket(ticket2["id"])
print(f"Closed ticket 2")

# Show tickets after closing
remaining_tickets = r1.get_tickets()
print(f"Remaining active tickets: {remaining_tickets}")
assert len(remaining_tickets) == 1, "Should have 1 active ticket after closing second ticket (test ticket still open)"

# Test order status updates
print(f"\n--- Testing Order Status Updates ---") 
print("Order status updates require active tickets -skipping for now")

# Test menu item management
print(f"\n--- Testing Menu Item Management ---")
new_item = MenuItem(100, "New Item", 15.99, "entrees", "A new menu item", [Ingredient(3, "Beef", 0.5, "lbs")])
added = r1.order_manager.add_menu_item(new_item)
print(f"Added new menu item: {added}")
assert added == True, "Menu item should be added successfully"

# Test getting menu item
menu_item = r1.order_manager.get_menu_item(100)
print(f"Retrieved menu item: {menu_item.to_dict() if menu_item else 'Not found'}")
assert menu_item is not None, "Menu item should be found"
assert menu_item.name == "New Item", "Menu item should have correct name"
assert menu_item.price == 15.99, "Menu item should have correct price"

# Test updating menu item
updated = r1.order_manager.update_menu_item(100, price=18.99, available=False)
print(f"Updated menu item: {updated}")
assert updated == True, "Menu item should update successfully"

# Test setting item availability
availability_set = r1.order_manager.set_item_availability(100, True)
print(f"Set item availability: {availability_set}")
assert availability_set == True, "Item availability should be set successfully"

print(f"\n--- Final State ---")
print(f"Final inventory: {r1.get_inventory()}")
print(f"Final menu: {r1.get_menu()}")
print(f"Final active tickets: {r1.get_tickets()}")
print(f"Final orders: {r1.get_orders()}")

# Final assertions
assert len(r1.get_inventory()) > 0, "Should have inventory items"
assert len(r1.get_menu()) > 0, "Should have menu items"
assert len(r1.get_tickets()) == 1, "Should have 1 active ticket (test ticket)"
assert len(r1.get_orders()) == 0, "Should have no orders (all in closed tickets)"

print("\nAll tests passed! The restaurant system is working correctly.")
