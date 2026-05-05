import feedparser
import requests
import json
import os
import subprocess

# 🔐 from GitHub Secrets
BOT_TOKEN = os.getenv("BOT_NATI")
CHAT_ID = os.getenv("CHAT_ID_NATI")

RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCmX4nKaKkDunvLIgZUVDs3A"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
LAST_FILE = "last_video.json"


# 📥 Load last video ID
def load_last():
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r") as f:
            return json.load(f).get("id")
    return None


# 💾 Save last video ID
def save_last(video_id):
    with open(LAST_FILE, "w") as f:
        json.dump({"id": video_id}, f)


# 📤 Push file to GitHub (to persist state)
def push_changes():
    try:
        subprocess.run(["git", "config", "--global", "user.email", "bot@example.com"])
        subprocess.run(["git", "config", "--global", "user.name", "bot"])

        subprocess.run(["git", "add", LAST_FILE])
        subprocess.run(["git", "commit", "-m", "update last video"], check=False)
        subprocess.run(["git", "push"], check=False)
    except Exception as e:
        print("Git push error:", e)


# 📩 Send to Telegram
def send_post(title, link, thumbnail):
    url = f"{BASE_URL}/sendPhoto"

    caption = f"📺 <b>{title}</b>\n\n🔗 {link}"

    data = {
        "chat_id": CHAT_ID,
        "caption": caption,
        "parse_mode": "HTML"
    }

    try:
        img = requests.get(thumbnail).content
        files = {"photo": ("img.jpg", img)}
        res = requests.post(url, data=data, files=files)
        print(res.text)
    except Exception as e:
        print("Send error:", e)


# 🔁 Check new video
def check_new_video():
    feed = feedparser.parse(RSS_URL)

    if not feed.entries:
        print("No entries found")
        return

    latest = feed.entries[0]

    video_id = latest.yt_videoid
    title = latest.title
    link = latest.link
    thumbnail = latest.media_thumbnail[0]["url"]

    last_id = load_last()

    if video_id == last_id:
        print("No new video")
        return

    print("New video:", title)

    send_post(title, link, thumbnail)
    save_last(video_id)
    push_changes()


# ▶️ Run once (GitHub handles scheduling)
if __name__ == "__main__":
    try:
        check_new_video()
    except Exception as e:
        print("Error:", e)
