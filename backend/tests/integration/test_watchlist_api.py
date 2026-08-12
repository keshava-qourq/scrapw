import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.api.v1.watchlist import get_watchlist_service
from app.main import app
from app.schemas.watchlist import WatchlistGroup, WatchlistItemRead
from app.services.watchlist_service import normalize_group_key


class FakeWatchlistService:
    def __init__(self):
        self.items: dict[uuid.UUID, WatchlistItemRead] = {}

    async def add_item(self, data):
        item = WatchlistItemRead(
            id=uuid.uuid4(),
            product_name=data.product_name.strip(),
            group_key=normalize_group_key(data.product_name),
            marketplace=data.marketplace,
            price=data.price,
            rating=data.rating,
            url=data.url,
            notes=data.notes,
            created_at=datetime.now(timezone.utc),
        )
        self.items[item.id] = item
        return item

    async def delete_item(self, item_id):
        self.items.pop(item_id, None)

    async def list_groups(self):
        groups: dict[str, list[WatchlistItemRead]] = {}
        for item in self.items.values():
            groups.setdefault(item.group_key, []).append(item)
        result = []
        for key, items in groups.items():
            items = sorted(items, key=lambda i: i.price)
            rated = [i for i in items if i.rating is not None]
            best_rated = max(rated, key=lambda i: i.rating) if rated else None
            result.append(
                WatchlistGroup(
                    group_key=key,
                    product_name=items[0].product_name,
                    items=items,
                    lowest_price_item_id=items[0].id,
                    highest_rated_item_id=best_rated.id if best_rated else None,
                )
            )
        return result


def test_add_and_list_watchlist_groups_sorted_by_price():
    fake = FakeWatchlistService()
    app.dependency_overrides[get_watchlist_service] = lambda: fake
    try:
        with TestClient(app) as client:
            client.post(
                "/api/v1/watchlist",
                json={"product_name": "iPhone 15 128GB", "marketplace": "Amazon", "price": 65000, "rating": 4.5, "url": "https://amazon.in/x"},
            )
            client.post(
                "/api/v1/watchlist",
                json={"product_name": "iphone 15   128gb", "marketplace": "Flipkart", "price": 62000, "rating": 4.2, "url": "https://flipkart.com/x"},
            )
            response = client.get("/api/v1/watchlist/groups")
    finally:
        app.dependency_overrides.pop(get_watchlist_service, None)

    assert response.status_code == 200
    groups = response.json()
    assert len(groups) == 1
    group = groups[0]
    assert len(group["items"]) == 2
    assert group["items"][0]["marketplace"] == "Flipkart"
    assert group["items"][0]["price"] == 62000
    lowest = next(i for i in group["items"] if i["id"] == group["lowest_price_item_id"])
    assert lowest["marketplace"] == "Flipkart"


def test_add_watchlist_item_requires_positive_price():
    fake = FakeWatchlistService()
    app.dependency_overrides[get_watchlist_service] = lambda: fake
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/watchlist",
                json={"product_name": "Widget", "marketplace": "Amazon", "price": -5, "url": "https://example.com"},
            )
    finally:
        app.dependency_overrides.pop(get_watchlist_service, None)

    assert response.status_code == 422


def test_delete_watchlist_item():
    fake = FakeWatchlistService()
    app.dependency_overrides[get_watchlist_service] = lambda: fake
    try:
        with TestClient(app) as client:
            add_response = client.post(
                "/api/v1/watchlist",
                json={"product_name": "Widget", "marketplace": "Amazon", "price": 100, "url": "https://example.com"},
            )
            item_id = add_response.json()["id"]
            delete_response = client.delete(f"/api/v1/watchlist/{item_id}")
            groups_response = client.get("/api/v1/watchlist/groups")
    finally:
        app.dependency_overrides.pop(get_watchlist_service, None)

    assert delete_response.status_code == 204
    assert groups_response.json() == []
