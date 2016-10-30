import telebot
import requests
from telebot import types

UVI_BASE_PATH="http://api.openweathermap.org/v3/uvi/"
OPENWEATHERMAP_API_TOKEN = "<YOUR OPENWEATHERMAP TOKEN>"
locations = {}

bot = telebot.TeleBot("<YOUR TELEGRAM BOT TOKEN>")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, build_help_message())
    
@bot.message_handler(content_types=['location'])
def update_location(message):
    bot.send_chat_action(message.chat.id, "find_location")
    global locations
    user_location = "{0},{1}".format(round(message.location.latitude, 1), round(message.location.longitude, 1))
    locations[message.from_user.id] = user_location;
    bot.reply_to(message, "Your location is updated to {0}".format(user_location))
    
@bot.message_handler(commands=['uvi'])
def get_uvi_status(message):
    user_id = message.from_user.id
    global locations
    if user_id in locations:
        r = requests.get("{0}{1}/current.json?appid={2}".format(UVI_BASE_PATH, locations[user_id], OPENWEATHERMAP_API_TOKEN))
    
        if r.status_code == 200:
            uvi_index = r.json()["data"]
            uvi_description = process_uvi_index(uvi_index)
            bot.reply_to(message, "Current UVI index is {0} ({1})".format(uvi_description, uvi_index))
        else:
            bot.reply_to(message, "Hummm, sorry I don't have data for that location")
    else:
        bot.reply_to(message, "Sorry, I don't know where you are.\nYou need to send me your location in private first.")

@bot.message_handler(commands=['table'])
def get_uvi_table(message):
    bot.reply_to(message, build_uvi_table_message())
    
@bot.message_handler(commands=['forgetme'])
def forget_me(message):
    user_id = message.from_user.id
    global locations
    if user_id in locations:
        del locations[message.from_user.id]
        bot.reply_to(message, "Your location has been deleted!")
    else:
        bot.reply_to(message, "I can't do that since I don't know your location")
    
@bot.message_handler(commands=['location'])
def get_location(message):
    user_id = message.from_user.id
    global locations
    if user_id in locations:
        user_location = locations[user_id]
        bot.reply_to(message, "You latest sent location is {0}".format(user_location))
    else:
        bot.reply_to(message, "Sorry, I don't know your location")
    
def process_uvi_index(uvi_index):
    if uvi_index < 3:
        uvi_description = "very low"
    elif uvi_index < 5:
        uvi_description = "low"
    elif uvi_index < 7:
        uvi_description = "medium"
    elif uvi_index < 10:
        uvi_description = "high"
    else:
        uvi_description = "very high"
    return uvi_description
    
def build_help_message():
    return "\n \
I'm the UVI bot and I can help you to find out the strength of the sun's ultraviolet radiation (UVI) for a given location.\n \
\n \
You can control me by sending these commands: \n \
\n \
/uvi - get the UVI for your location (send me your location in private first) \n \
/location - get the latest location you sent to me \n \
/forgetme - delete your location \n \
/table - get the table I use to know whether the UVI is low/medium/high/... \n \
\n"
             
def build_uvi_table_message():
    return "\n \
I base my comments on the UVI on this table: \n \
\n \
[0 - 3] - very low \n \
[3 - 5] - low \n \
[5 - 7] - medium \n \
[7 - 10] - high \n \
10+ - very high \n \
\n"
    
bot.polling(none_stop=True)
