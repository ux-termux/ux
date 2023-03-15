"""Plugin to manage federations"""
# Author: Copyright (C) 2020 KenHV [https://github.com/KenHV]

# For USERGE-X
# Ported to Pyrogram + Rewrite with Mongo DB
# by: (TG - @DeletedUser420) [https://github.com/code-rgb]
# Thanks @Lostb053  for writing help
# plugin modified for USERGE-X by @Kakashi_HTK(TG)/@ashwinstr(GH)
# before porting please ask to Kakashi

import asyncio
import os

from pyrogram import filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserBannedInChannel

from userge import Config, Message, get_collection, userge
from userge.helpers import extract_id, report_user

FBAN_LOG_CHANNEL = os.environ.get("FBAN_LOG_CHANNEL")

SAVED_SETTINGS = get_collection("CONFIGS")
FED_LIST = get_collection("FED_LIST")
CHANNEL = userge.getCLogger(__name__)


async def _init() -> None:
    f_t = await SAVED_SETTINGS.find_one({"_id": "FBAN_TAG"})
    if f_t:
        Config.FBAN_TAG = f_t["data"]


@userge.on_cmd(
    "fban_tag",
    about={
        "header": "enable / disable fbanner's tag",
        "flags": {
            "-c": "check",
        },
        "usage": "{tr}fban_tag",
    },
)
async def fban_sudo_tags(message: Message):
    """enable / disable fbanner's tag"""
    if not hasattr(Config, "FBAN_TAG"):
        setattr(Config, "FBAN_TAG", False)
    if "-c" in message.flags:
        if Config.FBAN_TAG:
            return await message.edit("`Fban tags are on.`", del_in=5)
        else:
            return await message.edit("`Fban tags are off.`", del_in=5)
    if Config.FBAN_TAG:
        Config.FBAN_TAG = False
        await message.edit("`Fban tags disabled.`", del_in=5)
    else:
        Config.FBAN_TAG = True
        await message.edit("`Fban tags enabled.`", del_in=5)
    await SAVED_SETTINGS.update_one(
        {"_id": "FBAN_TAG"}, {"$set": {"data": Config.FBAN_TAG}}, upsert=True
    )


async def _init() -> None:
    found = await SAVED_SETTINGS.find_one({"_id": "F_ADEL"})
    if found:
        Config.F_ADEL = found["switch"]
    else:
        Config.F_ADEL = False


@userge.on_cmd(
    "f_adel",
    about={
        "header": "toggle auto delete Fban confirmation",
        "flags": {
            "-c": "check",
        },
        "usage": "{tr}f_adel",
    },
)
async def f_adel(message: Message):
    if "-c" in message.flags:
        out_ = "ON" if Config.F_ADEL else "OFF"
        return await message.edit(
            f"`Fban confirmation auto-delete : {out_}.`", del_in=5
        )
    if Config.F_ADEL:
        Config.F_ADEL = False
        await SAVED_SETTINGS.update_one(
            {"_id": "F_ADEL"}, {"$set": {"switch": False}}, upsert=True
        )
    else:
        Config.F_ADEL = True
        await SAVED_SETTINGS.update_one(
            {"_id": "F_ADEL"}, {"$set": {"switch": True}}, upsert=True
        )
    out_ = "ON" if Config.F_ADEL else "OFF"
    await message.edit(f"`Fban confirmation auto-delete : {out_}.`")


@userge.on_cmd(
    "addf",
    about={
        "header": "Add a chat to fed list",
        "description": "Add a chat to fed list where message is to be sent",
        "usage": "{tr}addf",
    },
    allow_bots=False,
    allow_channels=False,
)
async def addfed_(message: Message):
    """Adds current chat to connected Feds."""
    chat_id = message.chat.id
    chat_t = await userge.get_chat(chat_id)
    chat_type = chat_t.type
    name = message.input_str or chat_t.title or chat_t.first_name
    if chat_type == "private":
        found = await FED_LIST.find_one({"schat_id": chat_id})
        if found:
            await message.edit(
                f"Chat __ID__: `{chat_id}`\nFed: **{found['sfed_name']}**\n\nAlready exists in Fed List !",
                del_in=7,
            )
            return
        await FED_LIST.insert_one(
            {"sfed_name": name, "schat_id": chat_id, "chat_type": chat_type}
        )
    else:
        found = await FED_LIST.find_one({"chat_id": chat_id})
        if found:
            await message.edit(
                f"Chat __ID__: `{chat_id}`\nFed: **{found['fed_name']}**\n\nAlready exists in Fed List !",
                del_in=7,
            )
            return
        await FED_LIST.insert_one(
            {"fed_name": name, "chat_id": chat_id, "chat_type": chat_type}
        )
    msg_ = f"__ID__ `{chat_id}` added to Fed: **{name}**"
    await message.edit(msg_, del_in=7)
    await CHANNEL.log(msg_)


@userge.on_cmd(
    "delf",
    about={
        "header": "Remove a chat from fed list",
        "flags": {"-all": "Remove all the feds from fedlist"},
        "description": "Remove a chat from fed list",
        "usage": "{tr}delf",
    },
    allow_bots=False,
    allow_channels=False,
)
async def delfed_(message: Message):
    """Removes current chat from connected Feds."""
    if "-all" in message.flags:
        msg_ = "**Disconnected from all connected federations!**"
        await message.edit(msg_, del_in=7)
        await FED_LIST.drop()
    else:
        try:
            chat_ = await message.client.get_chat(message.input_str or message.chat.id)
            chat_t = chat_.type
            chat_id = chat_.id
            chat_.title
        except (PeerIdInvalid, IndexError):
            chat_id = message.input_str
            id_ = chat_id.replace("-", "")
            if not id_.isdigit() or not chat_id.startswith("-"):
                return await message.err("Provide a valid chat ID...", del_in=7)
        out = f"Chat ID: {chat_id}\n"
        if chat_t == "private":
            found = await FED_LIST.find_one({"schat_id": int(chat_id)})
            if found:
                msg_ = out + f"Successfully Removed Fed: **{found['sfed_name']}**"
                await message.edit(msg_, del_in=7)
                await FED_LIST.delete_one(found)
            else:
                return await message.err(
                    out + "**Does't exist in your Fed List !**", del_in=7
                )
        else:
            found = await FED_LIST.find_one({"chat_id": int(chat_id)})
            if found:
                msg_ = out + f"Successfully Removed Fed: **{found['fed_name']}**"
                await message.edit(msg_, del_in=7)
                await FED_LIST.delete_one(found)
            else:
                return await message.err(
                    out + "**Does't exist in your Fed List !**", del_in=7
                )
    await CHANNEL.log(msg_)


@userge.on_cmd(
    "fban",
    about={
        "header": "Fban user",
        "description": "Fban the user from the list of fed",
        "flags": {
            "-d": "auto-delete message",
        },
        "usage": "{tr}fban [username|reply to user|user_id] [reason (optional)]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def fban_(message: Message):
    """Bans a user from connected Feds."""
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBanned {}</b>"]
    PROOF_CHANNEL = FBAN_LOG_CHANNEL if FBAN_LOG_CHANNEL else Config.LOG_CHANNEL_ID
    input = message.filtered_input_str
    await message.edit(fban_arg[0])
    sudo_ = False
    if (
        message.from_user.id in Config.SUDO_USERS
        or message.from_user.id in Config.TRUSTED_SUDO_USERS
    ):
        sudo_ = True
    if not message.reply_to_message:
        split_ = input.split(" ", 1)
        user = split_[0]
        if not user.isdigit() and not user.startswith("@"):
            user = extract_id(message.text)
        if len(split_) == 2:
            reason = split_[1]
        else:
            reason = "not specified"
    else:
        user = message.reply_to_message.from_user.id
        reason = input
        d_msg = message.reply_to_message
    if user is None:
        return await message.err("Provide a user ID or reply to a user...", del_in=7)
    try:
        user_ = await message.client.get_users(user)
        user = user_.id
    except (PeerIdInvalid, IndexError):
        pass
    if (
        user in Config.SUDO_USERS
        or user in Config.TRUSTED_SUDO_USERS
        or user in Config.OWNER_ID
        or user == (await message.client.get_me()).id
    ):
        if not input:
            await message.edit("Can't fban replied user, give user ID...", del_in=7)
            return
        user = input.split()[0]
        reason = input.split()[1:]
        reason = " ".join(reason)
        try:
            user_ = await message.client.get_users(user)
            user = user_.id
        except (PeerIdInvalid, IndexError):
            d_err = f"Failed to detect user **{user}**, fban might not work..."
            await message.edit(f"{d_err}\nType `y` to ontinue.")
            await CHANNEL.log(d_err)
            try:
                async with userge.conversation(message.chat.id) as conv:
                    response = await conv.get_response(
                        mark_read=True, filters=(filters.user([message.from_user.id]))
                    )
            except BaseException:
                return await message.edit(
                    f"`Fban terminated...\nReason: Response timeout.`"
                )
            if response.text == "y":
                pass
            else:
                return await message.edit(
                    f"`Fban terminated...\nReason: User didn't continue.`"
                )
        if (
            user in Config.SUDO_USERS
            or user in Config.OWNER_ID
            or user == (await message.client.get_me()).id
        ):
            return await message.err(
                "Can't fban user that exists in SUDO or OWNERS...", del_in=7
            )
    try:
        user_ = await userge.get_users(user)
        u_link = user_.mention
        u_id = user_.id
    except BaseException:
        u_link = user
        u_id = user
    failed = []
    total = 0
    reason = reason or "Not specified."
    await message.edit(fban_arg[1])
    async for data in FED_LIST.find():
        is_chat = True
        try:
            chat_id = int(data["chat_id"])
        except KeyError:
            chat_id = int(data["schat_id"])
            is_chat = False

        if is_chat:
            total += 1
            try:
                await userge.send_message(
                    chat_id,
                    f"/fban <a href='tg://user?id={user}'>{user}</a> {reason}",
                    disable_web_page_preview=True,
                )
            except UserBannedInChannel:
                pass
            try:
                async with userge.conversation(chat_id, timeout=8) as conv:
                    response = await conv.get_response(
                        mark_read=True,
                        filters=(
                            filters.user([609517172, 2059887769]) & ~filters.service
                        ),
                    )
                    resp = response.text
                    if not (
                        ("New FedBan" in resp)
                        or ("starting a federation ban" in resp)
                        or ("Starting a federation ban" in resp)
                        or ("start a federation ban" in resp)
                        or ("FedBan Reason update" in resp)
                        or ("FedBan reason updated" in resp)
                        or ("Would you like to update this reason?" in resp)
                    ):
                        failed.append(
                            f"{data['fed_name']}  \n__ID__: `{data['chat_id']}`"
                        )
                    if "Would you like to update this reason?" in resp:
                        await response.click("Update reason")
            except FloodWait as f:
                await asyncio.sleep(f.x + 3)
            except BaseException:
                failed.append(data["fed_name"])

        else:
            await userge.send_message(
                chat_id,
                f"{Config.FSUDO_TRIGGER}fban [{user}](tg://user?id={(user)}) {reason}",
                disable_web_page_preview=True,
            )

        await asyncio.sleep(0.1)

    if total == 0:
        return await message.err(
            "You Don't have any feds connected!\nsee .help addf, for more info."
        )

    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Failed to fban in {len(failed)}/{total} feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Success! Fbanned in `{total}` feds."
    msg_ = (
        fban_arg[3].format(u_link)
        + f"\n**ID:** <code>{u_id}</code>\n**Reason:** {reason}\n**Status:** {status}\n"
    )
    if sudo_:
        msg_ += f"**By:** {message.from_user.mention}"
    del_ = 3 if "-d" in message.flags or Config.F_ADEL else -1
    await message.edit(msg_, del_in=del_)
    await userge.send_message(int(PROOF_CHANNEL), msg_)
    try:
        check_me = await userge.get_chat_member(d_msg.chat.id, "me")
        if check_me.status in ["creator", "administrator"]:
            x = await d_msg.reply_text(f"!dban {reason}", disable_web_page_preview=True)
            await asyncio.sleep(10)
            await x.delete()
    except BaseException:
        pass


@userge.on_cmd(
    "fbanp",
    about={
        "header": "Fban with proof",
        "description": "Fban user from the list of feds with replied message as proof"
        "\nWARNING: don't use if any of the fed group has links blocklisted",
        "flags": {
            "-r": "remote fban, use with direct proof link",
            "-d": "auto-delete message",
        },
        "usage": "{tr}fbanp [direct reply to spammer] {reason}\n{tr}fbanp [reply to proof forwarded by you] {user id} {reason}",
    },
    allow_bots=False,
    allow_channels=False,
)
async def fban_p(message: Message):
    """Fban user from connected feds with proof."""
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBanned {}{}</b>"]
    d_err = ("Failed to detect user **{}**, fban might not work...",)
    if not FBAN_LOG_CHANNEL:
        await message.edit(
            "Add <code>FBAN_LOG_CHANNEL</code> to forward the proofs...", del_in=5
        )
        return
    try:
        channel_ = await userge.get_chat(int(FBAN_LOG_CHANNEL))
    except BaseException:
        return await message.edit(
            f"`The FBAN_LOG_CHANNEL ID provided ('{FBAN_LOG_CHANNEL}') is invalid, enter correct one.`",
            del_in=5,
        )
    if channel_.username is None or channel_.type != "channel":
        await message.edit(
            "Proof channel should be a <b>channel</b> and should be <b>public</b> for this command to work...",
            del_in=5,
        )
        return
    sudo_ = False
    if (
        message.from_user.id in Config.SUDO_USERS
        or message.from_user.id in Config.TRUSTED_SUDO_USERS
    ):
        sudo_ = True
    if "-r" in message.flags:
        link_ = message.filtered_input_str
        link_split = link_.split()
        link_ = link_split[0]
        try:
            reason = " ".join(link_split[1:])
        except BaseException:
            reason = "Not specified"
        try:
            user_and_message = link_.split("/")
            chat_id = user_and_message[-2]
            if chat_id.isdigit():
                chat_id = "-100" + str(chat_id)
                chat_id = int(chat_id)
            else:
                chat_ = await userge.get_chat(chat_id)
                chat_id = chat_.id
            msg_id = int(user_and_message[-1])
        except BaseException:
            await message.edit(
                "`Provide a proper spam message link to report...`", del_in=5
            )
            return
        try:
            msg_en = await userge.get_messages(chat_id, int(msg_id))
            user = msg_en.from_user.id
            proof = msg_en.message_id
        except BaseException:
            await message.edit(
                "`Provide a proper spam message link to report...`", del_in=5
            )
            return
        input = ""
    else:
        reply = message.reply_to_message
        if not reply:
            await message.err("Please reply to proof...", del_in=7)
            return
        chat_id = message.chat.id
        user = reply.from_user.id
        input = message.filtered_input_str
        reason = input
        msg_en = reply
        proof = msg_en.message_id
    fps = True
    if (
        user in Config.SUDO_USERS
        or user in Config.TRUSTED_SUDO_USERS
        or user in Config.OWNER_ID
        or user == (await message.client.get_me()).id
    ):
        fps = False
        if not input:
            await message.err(
                "Can't fban replied/specified user because of them being SUDO_USER or OWNER, give user ID...",
                del_in=5,
            )
            return
        split_ = input.split(" ", 1)
        user = split_[0]
        if not user.isdigit() and not user.startswith("@"):
            user = extract_id(message.text)
        try:
            user_ = await userge.get_users(user)
            user = user_.id
        except (PeerIdInvalid, IndexError):
            d_err = f"Failed to detect user **{user}**, fban might not work..."
            await message.edit(d_err, del_in=5)
            await CHANNEL.log(d_err)
        try:
            reason = split_[1]
        except BaseException:
            reason = "not specified"
        if (
            user in Config.SUDO_USERS
            or user in Config.OWNER_ID
            or user == (await message.client.get_me()).id
        ):
            return await message.err(
                "Can't fban user that exists in SUDO or OWNERS...", del_in=5
            )
    try:
        user_ = await userge.get_users(user)
        u_link = user_.mention
        u_id = user_.id
    except BaseException:
        u_link = user
        u_id = user
    await message.edit(fban_arg[0])
    failed = []
    r_update = []
    total = 0
    await message.edit(fban_arg[1])
    log_fwd = await userge.forward_messages(
        int(FBAN_LOG_CHANNEL),
        from_chat_id=chat_id,
        message_ids=proof,
    )
    reason = reason or "Not specified"
    reason += " || {" + f"{log_fwd.link}" + "}"
    if fps:
        report_user(
            chat=chat_id,
            user_id=user,
            msg=msg_en,
            msg_id=proof,
            reason=reason,
        )
        reported = "</b> and <b>reported "
    else:
        reported = ""
    async for data in FED_LIST.find():
        is_chat = True
        try:
            chat_id = int(data["chat_id"])
        except KeyError:
            chat_id = int(data["schat_id"])
            is_chat = False
        if is_chat:
            total += 1
            try:
                await userge.send_message(
                    chat_id,
                    f"/fban <a href='tg://user?id={user}'>{user}</a> {reason}",
                    disable_web_page_preview=True,
                )
            except UserBannedInChannel:
                pass
            try:
                async with userge.conversation(chat_id, timeout=8) as conv:
                    response = await conv.get_response(
                        mark_read=True,
                        filters=(
                            filters.user([609517172, 2059887769]) & ~filters.service
                        ),
                    )
                    resp = response.text
                    if not (
                        ("New FedBan" in resp)
                        or ("starting a federation ban" in resp)
                        or ("Starting a federation ban" in resp)
                        or ("start a federation ban" in resp)
                        or ("FedBan Reason update" in resp)
                        or ("FedBan reason updated" in resp)
                        or ("Would you like to update this reason?" in resp)
                    ):
                        failed.append(
                            f"{data['fed_name']}  \n__ID__: `{data['chat_id']}`"
                        )
                    if "Would you like to update this reason?" in resp:
                        await response.click("Update reason")
            except FloodWait as f:
                await asyncio.sleep(f.x + 3)
            except BaseException:
                failed.append(data["fed_name"])

        else:
            await userge.send_message(
                chat_id,
                f"{Config.FSUDO_TRIGGER}fban <a href='tg://user?id={user}'>{user}</a> {reason}",
                disable_web_page_preview=True,
            )

        await asyncio.sleep(0.1)
    if total == 0:
        return await message.err(
            "You Don't have any feds connected!\nsee .help addf, for more info."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Failed to fban in {len(failed)}/{total} feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"<b>Success!</b> Fbanned in {total} feds."
        if len(r_update) != 0:
            for i in r_update:
                status += f"\n• {i}"
    msg_ = (
        fban_arg[3].format(reported, u_link)
        + f"\n**ID:** <code>{u_id}</code>\n**Reason:** {reason}\n**Status:** {status}\n"
    )
    if sudo_:
        msg_ += f"**By:** {message.from_user.mention}"
    del_ = 3 if "-d" in message.flags or Config.F_ADEL else -1
    await message.edit(msg_, del_in=del_, disable_web_page_preview=True)
    await userge.send_message(
        int(FBAN_LOG_CHANNEL), msg_, disable_web_page_preview=True
    )
    try:
        check_me = await userge.get_chat_member(reply.chat.id, "me")
        if check_me.status in ["creator", "administrator"]:
            x = await reply.reply_text(f"!dban {reason}", disable_web_page_preview=True)
            await asyncio.sleep(10)
            await x.delete()
    except BaseException:
        pass


@userge.on_cmd(
    "fbanm",
    about={
        "header": "Mass fban a list of users",
        "description": "Mass fban replied list of users from the list of feds",
        "usage": "{tr}fbanm [reply to list of spammers] [reason (optional)]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def fban_m(message: Message):
    """Mass fban list of users."""
    if not message.reply_to_message:
        await message.edit("Reply to a list of users...", del_in=5)
        return
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>FBan complete</b>"]
    PROOF_CHANNEL = FBAN_LOG_CHANNEL if FBAN_LOG_CHANNEL else Config.LOG_CHANNEL_ID
    input = message.reply_to_message.text.split()
    reason = message.input_str or "Not specified"
    user_n = 0
    ban, cant = 0, 0
    fban_prog = fban_arg[0]
    for user in input:
        user_n += 1
        if user.startswith("@"):
            try:
                user_ = await message.client.get_users(user)
                user = user_.id
            except BaseException:
                pass
        if (
            user in Config.SUDO_USERS
            or user in Config.OWNER_ID
            or user == (await message.client.get_me()).id
        ):
            cant += 1
            continue
        fail = 0
        try:
            await mass_fban(user, reason)
        except BaseException:
            fail += 1
        ban += 1
        prog = user_n / len(input) * 100
        prog_1, prog_2 = True, True
        if prog >= 33 and prog_1:
            fban_prog = fban_arg[1]
            prog_1 = False
        if prog >= 66 and prog_2:
            fban_prog = fban_arg[2]
            prog_2 = False
        if prog == 100:
            fban_prog = fban_arg[3]
        await message.edit(
            f"{fban_prog}\n"
            f"**Fbanned:** {ban} out of {len(input)}\n"
            f"**Can't fban:** {cant}"
        )
        if user_n == len(input):
            await userge.send_message(
                PROOF_CHANNEL,
                f"#FBAN\n**Fbanned:** {ban} out of {len(input)}\n**Failed:** {fail}\n**Can't fban:** {cant}",
            )


@userge.on_cmd(
    "unfban",
    about={
        "header": "Unfban user",
        "description": "Unfban the user from the list of fed",
        "usage": "{tr}unfban [username|reply to user|user_id]",
    },
    allow_bots=False,
    allow_channels=False,
)
async def unfban_(message: Message):
    """Unbans a user from connected Feds."""
    user = (message.extract_user_and_text)[0]
    fban_arg = ["❯", "❯❯", "❯❯❯", "❯❯❯ <b>Un-FBanned {}</b>"]
    await message.edit(fban_arg[0])
    input = message.input_str
    if message.reply_to_message:
        reason = input
    else:
        try:
            reason = input.split(" ", 1)[1]
        except BaseException:
            reason = "not specified, maybe they solved it out"
    PROOF_CHANNEL = FBAN_LOG_CHANNEL if FBAN_LOG_CHANNEL else Config.LOG_CHANNEL_ID
    error_msg = "Provide a User ID or reply to a User"
    if user is None:
        return await message.err(error_msg, del_in=7)
    try:
        user_ = await message.client.get_users(user)
    except (PeerIdInvalid, IndexError):
        return await message.err(error_msg, del_in=7)
    user = user_.id
    reason = reason or "Not specified"
    failed = []
    total = 0
    await message.edit(fban_arg[1])
    async for data in FED_LIST.find():
        is_chat = True
        try:
            chat_id = int(data["chat_id"])
        except KeyError:
            chat_id = int(data["schat_id"])
            is_chat = False
        if is_chat:
            total += 1
            try:
                async with userge.conversation(chat_id, timeout=8) as conv:
                    await conv.send_message(f"/unfban {user} {reason}")
                    response = await conv.get_response(
                        mark_read=True,
                        filters=(
                            filters.user([609517172, 2059887769]) & ~filters.service
                        ),
                    )
                    resp = response.text
                    if (
                        ("New un-FedBan" not in resp)
                        and ("I'll give" not in resp)
                        and ("Un-FedBan" not in resp)
                    ):
                        failed.append(
                            f"{data['fed_name']}  \n__ID__: `{data['chat_id']}`"
                        )
            except FloodWait as f:
                await asyncio.sleep(f.x + 3)
            except BaseException:
                failed.append(data["fed_name"])

        else:
            await userge.send_message(
                chat_id,
                f"{Config.FSUDO_TRIGGER}unfban <a href='tg://user?id={user}'>{user}</a> {reason}",
                disable_web_page_preview=True,
            )

        await asyncio.sleep(0.1)
    if total == 0:
        return await message.err(
            "You Don't have any feds connected!\nsee .help addf, for more info."
        )
    await message.edit(fban_arg[2])

    if len(failed) != 0:
        status = f"Failed to un-fban in `{len(failed)}/{total}` feds.\n"
        for i in failed:
            status += "• " + i + "\n"
    else:
        status = f"Success! Un-Fbanned in `{total}` feds."
    msg_ = (
        fban_arg[3].format(user_.mention)
        + f"\n<b>ID:</b> <code>{user}</code>\n<b>Reason:</b> {reason}\n**Status:** {status}"
    )
    await message.edit(msg_)
    await userge.send_message(int(PROOF_CHANNEL), msg_)


@userge.on_cmd(
    "listf",
    about={
        "header": "Fed Chat List",
        "description": "Get a list of chats added in fed",
        "flags": {
            "-id": "Show fed group id in list.",
        },
        "usage": "{tr}listf",
    },
)
async def fban_lst_(message: Message):
    """List all connected Feds."""
    out = ""
    total = 0
    async for data in FED_LIST.find():
        is_chat = True
        try:
            chat_id = int(data["chat_id"])
        except KeyError:
            chat_id = int(data["schat_id"])
            is_chat = False
        if is_chat:
            total += 1
            id_ = f"'<code>{chat_id}</code>' - " if "-id" in message.flags else ""
            out += f"• Fed: {id_}<b>{data['fed_name']}</b>\n"
        else:
            out += f"\n• SUDO FED : <b>{data['sfed_name']}</b>\n"
    await message.edit_or_send_as_file(
        f"**Connected federations: [{total}]**\n\n" + out
        if out
        else "**You haven't connected to any federations yet!**",
        caption="Connected Fed List",
    )


async def mass_fban(user, reason):
    async for data in FED_LIST.find():
        chat_id = int(data["chat_id"])
        try:
            await userge.send_message(chat_id, f"/fban {user} {reason}")
            await asyncio.sleep(0.5)
        except FloodWait as e:
            await asyncio.sleep(e.x + 5)
