from bot.bot import Bot
from data_unit import DataUnit
from storage.storage_manager import storage_manager


# start firebase
storage_manager.start_firebase()

# last
last_data = DataUnit().fill_data_from_gsheets()

# viber bot Singleton init
bot = Bot(storage_manager.get_storage_strategy(),
          storage_manager.get_sheets_service())

viber = bot.viber

bot.message_manager.populate_daily_data()
