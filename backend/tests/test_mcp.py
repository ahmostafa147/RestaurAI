import asyncio
import json
from server import list_tools, call_tool

async def test():
    print(f"Tools: {[t.name for t in await list_tools()]}\n")

    result = await call_tool("create_restaurant", {"name": "Test Diner"})
    print(f"Create: {result[0].text}\n")
    key = json.loads(result[0].text)["key"]

    result = await call_tool("get_menu", {"key": key})
    print(f"Menu: {result[0].text}\n")

    result = await call_tool("reserve_table", {"key": key, "name": "Bob", "party_size": 3, "time": "6:00 PM"})
    print(f"Reservation: {result[0].text}\n")

    result = await call_tool("place_order", {"key": key, "table_number": 2, "item_ids": [1, 3, 7]})
    print(f"Order: {result[0].text}\n")

    result = await call_tool("get_reservations", {"key": key})
    print(f"Reservations: {result[0].text}\n")

    result = await call_tool("get_orders", {"key": key})
    print(f"Orders: {result[0].text}")

asyncio.run(test())
