from datetime import datetime

from flask import Flask, jsonify, request

app = Flask(__name__)

announcements = {}
id_counter = 0


@app.route("/api/announcements", methods=["GET"])
def get_announcements():
    return jsonify(list(announcements.values())), 200


@app.route("/api/announcements/<int:announcement_id>", methods=["GET"])
def get_announcement(announcement_id):
    announcement = announcements.get(announcement_id)
    if not announcement:
        return jsonify({"error": "Announcement not found"}), 404
    return jsonify(announcement), 200


@app.route("/api/announcements", methods=["POST"])
def create_announcement():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    title = data.get("title")
    description = data.get("description")
    owner = data.get("owner")

    if not title or not description or not owner:
        return jsonify({"error": "Title, description, and owner are required"}), 400

    global id_counter
    id_counter += 1
    announcement_id = id_counter
    announcement = {
        "id": announcement_id,
        "title": title,
        "description": description,
        "owner": owner,
        "created_at": datetime.utcnow().isoformat(),
    }
    announcements[announcement_id] = announcement
    return jsonify(announcement), 201


@app.route("/api/announcements/<int:announcement_id>", methods=["PUT"])
def update_announcement(announcement_id):
    announcement = announcements.get(announcement_id)
    if not announcement:
        return jsonify({"error": "Announcement not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    if "title" in data:
        announcement["title"] = data["title"]
    if "description" in data:
        announcement["description"] = data["description"]
    if "owner" in data:
        announcement["owner"] = data["owner"]

    return jsonify(announcement), 200


@app.route("/api/announcements/<int:announcement_id>", methods=["DELETE"])
def delete_announcement(announcement_id):
    announcement = announcements.get(announcement_id)
    if not announcement:
        return jsonify({"error": "Announcement not found"}), 404

    del announcements[announcement_id]
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
