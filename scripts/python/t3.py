import asyncio
import logging
import os
import shutil
from datetime import datetime
from json import dump
from pytdbot import VERSION, Client, types


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.StreamHandler()
    ]
)


TG_API_ID = int(os.environ.get("TG_API_ID", "6"))
TG_API_HASH = os.environ.get("TG_API_HASH", "")
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
TG_MESSAGE_LINK = os.environ.get("TG_MESSAGE_LINK", "")


async def main():
    d = {}
    d["version"] = VERSION
    d["layer"] = types.TDLIB_VERSION
    f = "LevLam"
    client = Client(
        token=TG_BOT_TOKEN,
        api_id=TG_API_ID,
        api_hash=TG_API_HASH,
        database_encryption_key="cucumber",
        files_directory=f,
        use_file_database=False,
        # use_chat_info_database=False,
        use_message_database=False,
        # no_updates=True,
        default_parse_mode="html",
        # options={
        #     "disable_network_statistics": True,
        #     "disable_time_adjustment_protection": True,
        #     "ignore_inline_thumbnails": True,
        #     "ignore_background_updates": True,
        #     "message_unload_delay": 60,
        #     "disable_persistent_network_statistics": True,
        # },
        td_verbosity=3,  # TDLib verbosity level
    )
    await client.start()
    internalLinkInfo = await client.invoke({
        "@type": "getInternalLinkType",
        "link": TG_MESSAGE_LINK
    })
    messageLinkInfo = await client.invoke({
        "@type": "getMessageLinkInfo",
        "url": internalLinkInfo.url
    })
    d["file_size"] = messageLinkInfo.message.content.document.document.size
    t2 = datetime.now()
    m = await client.invoke({
        "@type": "downloadFile",
        "file_id": messageLinkInfo.message.content.document.document.id,
        "priority": 1,
        "offset": 0,
        "limit": 0,
        "synchronous": True,
    })
    t3 = datetime.now()
    d["download"] = {
        "start_time": t2.timestamp(),
        "end_time": t3.timestamp(),
        "time_taken": (t3 - t2).seconds
    }
    t4 = datetime.now()
    u = await client.sendDocument(
        chat_id=messageLinkInfo.chat_id,
        document=types.InputFileLocal(m.local.path),
        caption="pytdbot/client",
        reply_to_message_id=messageLinkInfo.message.id
    )
    t5 = datetime.now()
    d["upload"] = {
        "start_time": t4.timestamp(),
        "end_time": t5.timestamp(),
        "time_taken": (t5 - t4).seconds
    }
    await client.stop()
    shutil.rmtree(f, ignore_errors=True)
    with open("./outputs/pytdbot.json", "w", encoding="utf-8") as f:
        dump(d, f, ensure_ascii=False, indent=2)


# We need a loop to work with
loop = asyncio.get_event_loop()
# Then, we need to run the loop with a task
loop.run_until_complete(main())
