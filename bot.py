import os
import asyncio
import discord
import feedparser
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

POST_CHECK_INTERVAL = 300  # 5 minutes

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# List of RSS feeds to monitor
RSS_FEEDS = {
    "AnimeHunch": "https://animehunch.com/feed/",
    "Crunchyroll": "https://www.crunchyroll.com/rss/anime?lang=en",
    "ANN": "https://www.animenewsnetwork.com/all/rss.xml",
    "AnimeCorner": "https://animecorner.me/feed/",
    "ComicBook": "https://comicbook.com/category/anime/rss/",
    "AnimeAnime": "https://s.animeanime.jp/category/news/feed/",
    "MyAnimeForLife": "https://www.myanimeforlife.com/category/news/feed/",
}


# Store links already posted
posted_links = {name: set() for name in RSS_FEEDS}

async def check_feeds(channel):
    try:
        while True:
            for name, url in RSS_FEEDS.items():
                feed = feedparser.parse(url)
                if not feed.entries:
                    continue

                # Get the latest 3 entries
                new_entries = []
                for entry in feed.entries[:3]:
                    if entry.link not in posted_links[name]:
                        new_entries.append(entry)
                        posted_links[name].add(entry.link)

                for entry in reversed(new_entries):
                    await channel.send(f"📢 **[{name}] {entry.title}**\n{entry.link}")

            await asyncio.sleep(POST_CHECK_INTERVAL)
    except Exception as e:
        print(f"⚠️ Error in check_feeds: {e}")

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"❌ Could not find channel with ID {CHANNEL_ID}")
        return
    asyncio.create_task(check_feeds(channel))

if __name__ == "__main__":
    asyncio.run(client.start(DISCORD_TOKEN))
