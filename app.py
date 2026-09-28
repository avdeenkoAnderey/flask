import asyncio
from datetime import datetime, timezone
from aiohttp import web

announcements = {}
id_counter = 0
lock = asyncio.Lock()


async def get_announcements(request):
    async with lock:
        return web.json_response(list(announcements.values()))


async def get_announcement(request):
    announcement_id = int(request.match_info["id"])
    async with lock:
        announcement = announcements.get(announcement_id)
    if not announcement:
        return web.json_response({"error": "Announcement not found"}, status=404)
    return web.json_response(announcement)


async def create_announcement(request):
    global id_counter
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

    async with lock:
        id_counter += 1
        announcement_id = id_counter
        announcement = {
            "id": announcement_id,
            "title": title,
            "description": description,
            "owner": owner,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        announcements[announcement_id] = announcement

    return web.json_response(announcement, status=201)


async def update_announcement(request):
    announcement_id = int(request.match_info["id"])
    async with lock:
        announcement = announcements.get(announcement_id)
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

    async with lock:
        if "title" in data:
            announcement["title"] = data["title"]
        if "description" in data:
            announcement["description"] = data["description"]
        if "owner" in data:
            announcement["owner"] = data["owner"]

    return web.json_response(announcement)


async def delete_announcement(request):
    announcement_id = int(request.match_info["id"])
    async with lock:
        announcement = announcements.get(announcement_id)
        if announcement:
            del announcements[announcement_id]
    if not announcement:
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
