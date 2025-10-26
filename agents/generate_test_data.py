#!/usr/bin/env python3
"""
Restaurant Test Data Generator

Generates realistic menu items, ingredients, and ticket history for both
Causwells and Cote Ouest Bistro restaurants defined in restaurants.json.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.src.core.restaurant import Restaurant
from backend.src.models.menu import MenuItem
from backend.src.models.ingredient import Ingredient


def load_restaurants() -> List[Dict[str, Any]]:
    """Load restaurant configuration from restaurants.json"""
    restaurants_file = os.path.join(os.path.dirname(__file__), 'restaurants.json')
    with open(restaurants_file, 'r') as f:
        config = json.load(f)
        return config.get('restaurants', [])


def create_causwells_menu() -> Dict[str, List[MenuItem]]:
    """Create menu items for Causwells (American Brunch/Comfort Food)"""
    menu = {
        "Appetizers": [
            MenuItem(1, "Deviled Eggs", 8.50, "Appetizers", "Classic deviled eggs with paprika", True, []),
            MenuItem(2, "Chicken Wings", 12.00, "Appetizers", "Buffalo wings with ranch dip", True, []),
            MenuItem(3, "Fried Pickles", 7.50, "Appetizers", "Crispy fried pickles with aioli", True, [])
        ],
        "Entrees": [
            MenuItem(4, "Classic Burger", 15.00, "Entrees", "Beef burger with lettuce, tomato, onion", True, []),
            MenuItem(5, "Fried Chicken Sandwich", 14.50, "Entrees", "Crispy chicken breast with slaw", True, []),
            MenuItem(6, "Mac & Cheese", 13.00, "Entrees", "Creamy mac and cheese with breadcrumbs", True, []),
            MenuItem(7, "Ribeye Steak", 28.00, "Entrees", "12oz ribeye with mashed potatoes", True, [])
        ],
        "Desserts": [
            MenuItem(8, "Chocolate Cake", 7.00, "Desserts", "Rich chocolate layer cake", True, []),
            MenuItem(9, "Apple Pie", 6.50, "Desserts", "Homemade apple pie with ice cream", True, []),
            MenuItem(10, "Vanilla Ice Cream", 4.00, "Desserts", "House-made vanilla ice cream", True, [])
        ],
        "Drinks": [
            MenuItem(11, "Coffee", 3.50, "Drinks", "Freshly brewed coffee", True, []),
            MenuItem(12, "Mimosa", 8.00, "Drinks", "Champagne and orange juice", True, []),
            MenuItem(13, "Craft Beer", 6.00, "Drinks", "Local craft beer selection", True, [])
        ]
    }
    return menu


def create_cote_ouest_menu() -> Dict[str, List[MenuItem]]:
    """Create menu items for Cote Ouest Bistro (French Bistro)"""
    menu = {
        "Appetizers": [
            MenuItem(1, "French Onion Soup", 9.50, "Appetizers", "Traditional soup with gruyere cheese", True, []),
            MenuItem(2, "Escargot", 14.00, "Appetizers", "Snails in garlic herb butter", True, []),
            MenuItem(3, "Pâté", 11.00, "Appetizers", "Duck liver pâté with cornichons", True, [])
        ],
        "Entrees": [
            MenuItem(4, "Coq au Vin", 24.00, "Entrees", "Chicken braised in red wine", True, []),
            MenuItem(5, "Steak Frites", 26.00, "Entrees", "Hanger steak with pommes frites", True, []),
            MenuItem(6, "Duck Confit", 28.00, "Entrees", "Slow-cooked duck leg with vegetables", True, []),
            MenuItem(7, "Ratatouille", 18.00, "Entrees", "Provençal vegetable stew", True, [])
        ],
        "Desserts": [
            MenuItem(8, "Crème Brûlée", 8.50, "Desserts", "Classic vanilla custard with caramelized sugar", True, []),
            MenuItem(9, "Tarte Tatin", 9.00, "Desserts", "Upside-down apple tart", True, []),
            MenuItem(10, "Profiteroles", 7.50, "Desserts", "Cream puffs with chocolate sauce", True, [])
        ],
        "Drinks": [
            MenuItem(11, "House Wine", 12.00, "Drinks", "Selection of French wines", True, []),
            MenuItem(12, "Espresso", 3.00, "Drinks", "Traditional French espresso", True, []),
            MenuItem(13, "Cognac", 15.00, "Drinks", "Premium French cognac", True, [])
        ]
    }
    return menu


def create_ingredients_for_menu(menu: Dict[str, List[MenuItem]]) -> Dict[int, Ingredient]:
    """Create realistic ingredients for all menu items"""
    ingredients = {}
    ingredient_id = 1
    
    # Common ingredients
    common_ingredients = [
        ("Salt", "oz", 0.10, "Basic Foods"),
        ("Pepper", "oz", 0.15, "Basic Foods"),
        ("Olive Oil", "oz", 0.25, "Mediterranean Imports"),
        ("Butter", "oz", 0.20, "Dairy Fresh"),
        ("Garlic", "oz", 0.30, "Fresh Produce"),
        ("Onion", "each", 0.50, "Fresh Produce"),
        ("Flour", "lbs", 0.80, "Baking Supplies"),
        ("Eggs", "each", 0.25, "Farm Fresh"),
        ("Milk", "cups", 0.15, "Dairy Fresh"),
        ("Cheese", "oz", 0.40, "Artisan Cheeses")
    ]
    
    # Add common ingredients
    for name, unit, cost, supplier in common_ingredients:
        ingredients[ingredient_id] = Ingredient(
            id=ingredient_id,
            name=name,
            quantity=random.uniform(50, 200),
            unit=unit,
            available=True,
            cost=cost,
            supplier=supplier
        )
        ingredient_id += 1
    
    # Add specific ingredients for each menu item
    for category, items in menu.items():
        for item in items:
            # Add 2-4 ingredients per menu item
            num_ingredients = random.randint(2, 4)
            for _ in range(num_ingredients):
                ingredient_name = f"{item.name} Ingredient {len([i for i in ingredients.values() if item.name in i.name]) + 1}"
                ingredients[ingredient_id] = Ingredient(
                    id=ingredient_id,
                    name=ingredient_name,
                    quantity=random.uniform(10, 100),
                    unit=random.choice(["oz", "lbs", "each", "cups"]),
                    available=True,
                    cost=random.uniform(0.50, 5.00),
                    supplier=random.choice(["Premium Foods", "Local Suppliers", "Artisan Imports"])
                )
                ingredient_id += 1
    
    return ingredients


def generate_ticket_history(restaurant: Restaurant, num_tickets: int = 75) -> List[Dict]:
    """Generate realistic ticket history for a restaurant"""
    tickets = []
    menu_items = restaurant.get_menu_dict()
    all_items = []
    
    # Flatten menu items
    for category, items in menu_items.items():
        for item in items:
            all_items.append(item)
    
    if not all_items:
        print(f"Warning: No menu items found for restaurant {restaurant.name}")
        return tickets
    
    # Generate tickets over the past 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for i in range(num_tickets):
        # Random timestamp within last 30 days
        random_days = random.uniform(0, 30)
        random_hours = random.uniform(10, 22)  # Restaurant hours
        ticket_time = start_date + timedelta(days=random_days, hours=random_hours)
        
        # Create ticket
        table_number = random.randint(1, 10)
        ticket_result = restaurant.create_ticket(table_number)
        
        if 'error' in ticket_result:
            print(f"Error creating ticket: {ticket_result['error']}")
            continue
            
        ticket_id = ticket_result['id']
        
        # Add 1-5 random items to ticket
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            item = random.choice(all_items)
            order_result = restaurant.place_order(table_number, item['id'], ticket_id)
            
            if 'error' in order_result:
                print(f"Error placing order: {order_result['error']}")
        
        # Close ticket
        ticket = restaurant.get_ticket(ticket_id) #Get ticket before it closes
        close_result = restaurant.close_ticket(ticket_id)

        if close_result:
            if ticket:
                tickets.append({
                    'ticket_id': ticket_id,
                    'table_number': table_number,
                    'timestamp': ticket_time.isoformat(),
                    'total': ticket.get('total', 0),
                    'items_ordered': num_items
                })
        else:
            print(f"Error closing ticket {ticket_id}")
    
    return tickets


def populate_restaurant_data(restaurant_config: Dict[str, Any]) -> Dict[str, Any]:
    """Populate database with menu, ingredients, and ticket history for a restaurant"""
    print(f"\nSetting up {restaurant_config['name']} ({restaurant_config['id']})...")
    
    # Create restaurant instance using hardcoded key
    restaurant = Restaurant(name=restaurant_config['name'], key=restaurant_config['secure_key'])
    
    print(f"  Created restaurant with key: {restaurant.key}")
    
    # Create menu based on restaurant type
    if 'causwells' in restaurant_config['id'].lower():
        menu = create_causwells_menu()
    elif 'cote' in restaurant_config['id'].lower():
        menu = create_cote_ouest_menu()
    else:
        print(f"Unknown restaurant type: {restaurant_config['id']}")
        return {}
    
    # Add menu items
    menu_items_added = 0
    for category, items in menu.items():
        for item in items:
            success = restaurant.add_menu_item(item)
            if success:
                menu_items_added += 1
            else:
                print(f"Failed to add menu item: {item.name}")
    
    print(f"  Added {menu_items_added} menu items")
    
    # Create and add ingredients
    ingredients = create_ingredients_for_menu(menu)
    ingredients_added = 0
    
    for ingredient in ingredients.values():
        success = restaurant.add_ingredient(ingredient)
        if success:
            ingredients_added += 1
        else:
            print(f"Failed to add ingredient: {ingredient.name}")
    
    print(f"  Added {ingredients_added} ingredients")
    
    # Generate ticket history
    print(f"  Generating ticket history...")
    tickets = generate_ticket_history(restaurant, num_tickets=75)
    print(f"  Generated {len(tickets)} closed tickets")
    
    return {
        'restaurant_id': restaurant_config['id'],
        'restaurant_name': restaurant_config['name'],
        'secure_key': restaurant_config['secure_key'],  # Use the hardcoded key
        'menu_items': menu_items_added,
        'ingredients': ingredients_added,
        'tickets': len(tickets),
        'total_revenue': sum(ticket['total'] for ticket in tickets)
    }


def main():
    """Main function to generate test data for all restaurants"""
    print("Restaurant Test Data Generator")
    print("=" * 50)
    
    # Load restaurant configurations
    restaurants = load_restaurants()
    print(f"Found {len(restaurants)} restaurants to populate")
    
    results = []
    
    # Populate data for each restaurant
    for restaurant_config in restaurants:
        # try:
        result = populate_restaurant_data(restaurant_config)
        if result:
            results.append(result)
        # except Exception as e:
        #     print(f"Error populating {restaurant_config['name']}: {e}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    total_menu_items = 0
    total_ingredients = 0
    total_tickets = 0
    total_revenue = 0
    
    for result in results:
        print(f"\n{result['restaurant_name']} ({result['restaurant_id']})")
        print(f"   Menu Items: {result['menu_items']}")
        print(f"   Ingredients: {result['ingredients']}")
        print(f"   Tickets: {result['tickets']}")
        print(f"   Revenue: ${result['total_revenue']:.2f}")
        print(f"   Secure Key: {result['secure_key']}")
        
        total_menu_items += result['menu_items']
        total_ingredients += result['ingredients']
        total_tickets += result['tickets']
        total_revenue += result['total_revenue']
    
    print(f"\nTOTALS")
    print(f"   Restaurants: {len(results)}")
    print(f"   Menu Items: {total_menu_items}")
    print(f"   Ingredients: {total_ingredients}")
    print(f"   Tickets: {total_tickets}")
    print(f"   Total Revenue: ${total_revenue:.2f}")
    
    print(f"\nTest data generation complete!")
    print(f"\nTo test the endpoints, run:")
    print(f"   python agents/test_endpoints.py")


if __name__ == "__main__":
    main()
