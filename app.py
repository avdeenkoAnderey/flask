import asyncio
from datetime import datetime, timezone
from aiohttp import web


class AsyncAnnouncementStore:
    def __init__(self):
        self._data = {}
        self._counter = 0
        self._lock = asyncio.Lock()

    async def get(self, announcement_id):
        async with self._lock:
            return self._data.get(announcement_id)

    async def get_all(self):
        async with self._lock:
            return list(self._data.values())

    async def create(self, announcement):
        async with self._lock:
            self._counter += 1
            announcement_id = self._counter
            self._data[announcement_id] = announcement
            return announcement_id

    async def update(self, announcement_id, data):
        async with self._lock:
            if announcement_id not in self._data:
                return None
            for key, value in data.items():
                self._data[announcement_id][key] = value
            return self._data[announcement_id]

    async def delete(self, announcement_id):
        async with self._lock:
            if announcement_id not in self._data:
                return None
            announcement = self._data.pop(announcement_id)
            return announcement

    async def get_all_ids(self):
        async with self._lock:
            return list(self._data.keys())


store = AsyncAnnouncementStore()


async def get_announcements(request):
    announcements = await store.get_all()
    return web.json_response(announcements)


async def get_announcement(request):
    announcement_id = int(request.match_info["id"])
    announcement = await store.get(announcement_id)
    if not announcement:
        return web.json_response({"error": "Announcement not found"}, status=404)
    return web.json_response(announcement)


async def create_announcement(request):
    data = await request.json()
    if not data:
        return web.json_response({"error": "No input data provided"}, status=400)

    title = data.get("title")
    description = data.get("description")
    owner = data.get("owner")

    if not title or not description or not owner:
        return web.json_response(
            {"error": "Title, description, and owner are required"}, status=400
        )

    announcement = {
        "id": 0,
        "title": title,
        "description": description,
        "owner": owner,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    announcement_id = await store.create(announcement)
    announcement["id"] = announcement_id

    return web.json_response(announcement, status=201)


async def update_announcement(request):
    announcement_id = int(request.match_info["id"])
    announcement = await store.get(announcement_id)
    if not announcement:
        return web.json_response({"error": "Announcement not found"}, status=404)

    data = await request.json()
    if not data:
        return web.json_response({"error": "No input data provided"}, status=400)

    if "title" in data and not data["title"]:
        return web.json_response(
            {"error": "Title cannot be empty"}, status=400
        )
    if "description" in data and not data["description"]:
        return web.json_response(
            {"error": "Description cannot be empty"}, status=400
        )
    if "owner" in data and not data["owner"]:
        return web.json_response(
            {"error": "Owner cannot be empty"}, status=400
        )

    updated = await store.update(announcement_id, data)

    return web.json_response(updated)


async def delete_announcement(request):
    announcement_id = int(request.match_info["id"])
    deleted = await store.delete(announcement_id)
    if not deleted:
        return web.json_response({"error": "Announcement not found"}, status=404)
    return web.Response(status=204)


def create_app():
    app = web.Application()
    app.router.add_get("/api/announcements", get_announcements)
    app.router.add_get("/api/announcements/{id}", get_announcement)
    app.router.add_post("/api/announcements", create_announcement)
    app.router.add_put("/api/announcements/{id}", update_announcement)
    app.router.add_delete("/api/announcements/{id}", delete_announcement)

    return app


if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=8080)
