from bot.bot import Bot
from data_unit import DataUnit
from start_data_loader import StartDataLoader
from storage.storage_manager import storage_manager


# start firebase
storage_manager.start_firebase()

# build boject for persistent data
start_data = StartDataLoader()

# viber bot Singleton init
bot = Bot(storage_manager.get_storage_strategy(),
          storage_manager.get_sheets_service(),
          start_data)


viber = bot.viber

# last_data = bot.message_manager.daily_builder.du

# # last
# last_data = DataUnit()
# last_data.fill_last_from_firebase_last()
# bot.message_manager.populate_daily_data()
