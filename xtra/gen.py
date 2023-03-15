import os
from pyrogram import Client
from pyrogram import __version__

if os.path.isfile("string.session"): os.remove("string.session")

API_ID = int(input("Enter API_ID: "))
API_HASH = input("Enter API_HASH: ")
pyro_ver = __version__

if pyro_ver == "1.4.7":
    client = Client(session_name="string",api_id=API_ID, api_hash=API_HASH)
else:
    client = Client(name='string', api_id=API_ID, api_hash=API_HASH, in_memory=True)

with client as app:
    str_session = app.export_session_string()
    app.send_message(
        "me",
       