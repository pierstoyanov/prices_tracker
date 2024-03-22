from bot.bot import Bot
from storage.storage_manager import storage_manager


# start firebase
storage_manager.firebase()

# Storage [firebase, gsheets, both]
storage_strategy = "both"

# viber bot Singleton init
bot = Bot(storage_strategy)
viber = bot.viber
