import os
import re

import requests
from bs4 import BeautifulSoup
from googlesearch import search

from userge import Message, userge
from userge.utils import post_to_telegraph


@userge.on_cmd(
    "lyrics",
    about={
        "header": "Genius Lyrics",
        "description": "Scrape Song Lyrics from Genius.com",
        "usage": "{tr}lyrics [Song Name]",
        "examples": "{tr}lyrics Swalla Nicki Minaj",
    },
)
async def lyrics(message: Message):
    song = message.input_str
    if not song:
        await message.edit("Bruh WTF?")
        return
    await message.edit(f"Searching lyrics for **{song}**...")
    to_search = song + "genius lyrics"
    gen_surl = list(search(to_search, num=1, stop=1))[0]
    gen_page = requests.get(gen_surl)
    scp = BeautifulSoup(gen_page.text, "html.parser")
    lyrics = scp.find("div", class_="lyrics")
    if not lyrics:
        await message.edit(f"No Results Found for: `{song}`")
        return
    lyrics = lyrics.get_text()
    lyrics = re.sub(r"[\(\[].*?[\)\]]", "", lyrics)
    lyrics = os.linesep.join((s for s in lyrics.splitlines() if s))
    title = scp.find("title").get_text().split("|")
    writers_box = [
        writer
        for writer in scp.find_all("span", {"class": "metadata_unit-label"})
        if writer.text == "Written By"
    ]
    if writers_box:
        target_node = writers_box[0].find_next_sibling(
            "span", {"class": "metadata_unit-info"}
        )
        writers = target_node.text.strip()
    else:
        writers = "UNKNOWN"
    lyr_format = ""
    lyr_format += "<b>" + title[0] + "</b>\n"
    lyr_format += "<i>" + lyrics + "</i>"
    lyr_format += "\n\n<b>Written By: </b>" + "<i>" + writers + "</i>"
    lyr_format += "\n<b>Source: </b>" + "`" + title[1] + "`"

    if lyr_format:
        if len(lyr_format) <= 4096:
            await message.edit(lyr_format)
        else:
            lyr_format = lyr_format.replace("\n", "<br>")
            link = post_to_telegraph(title[0], lyr_format)
            await message.edit(f"Posted the lyrics to telegraph...\n[Link]({link})")
    else:
        await message.edit(f"No Lyrics Found for **{song}**")
