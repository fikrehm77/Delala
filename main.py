import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot token and group/channel IDs
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Product management
products = {}
admin_group_id = -1002262363425  # Replace with your admin group ID
channel_id = -1002442298921  # Replace with your public channel ID

# Price increment options
PRICE_INCREMENTS = [5, 7.5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100,
                    125, 150, 175, 200, 250, 300, 350, 400, 450, 500, 600,
                    700, 800, 900, 1000]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_message = (
        "Welcome to the Buy & Sell Bot! "
        "Use the commands below to manage product listings.\n"
        "/sell - Start the selling process\n"
        "/help - View available commands"
    )
    bot.reply_to(message, welcome_message)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = (
        "Available commands:\n"
        "/sell - Start selling a product\n"
        "/help - List of commands"
    )
    bot.reply_to(message, help_message)

@bot.message_handler(commands=['sell'])
def start_sell(message):
    bot.reply_to(message, "Please send the product category, image, and your phone number in the format:\n"
                          "Category: <category_name>\nImage: <attach_image>\nPhone: <your_phone_number>")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    if chat_id not in products:
        products[chat_id] = {}

    if 'category' not in products[chat_id]:
        # Extract category and phone number from the previous message
        category_info = message.caption.splitlines()
        if len(category_info) < 2:
            bot.reply_to(message, "Please provide the category and phone number.")
            return
        
        category = category_info[0].replace("Category: ", "").strip()
        phone_number = category_info[1].replace("Phone: ", "").strip()

        products[chat_id]['category'] = category
        products[chat_id]['phone'] = phone_number
        products[chat_id]['photo_id'] = message.photo[-1].file_id

        # Create verification buttons
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("✅ Verify", callback_data=f"verify_{chat_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{chat_id}")
        )

        bot.send_message(admin_group_id, f"New product verification:\nCategory: {category}\nPhone: {phone_number}")
        bot.send_photo(admin_group_id, products[chat_id]['photo_id'], 
                       caption=f"Product for verification:\nCategory: {category}\nPhone: {phone_number}",
                       reply_markup=markup)
        bot.reply_to(message, "Your product submission has been received. Please wait for admin verification.")
    else:
        bot.reply_to(message, "You've already submitted a product. Please wait for the verification process.")

@bot.callback_query_handler(func=lambda call: call.data.startswith(('verify_', 'reject_')))
def handle_verification(call):
    action, user_chat_id = call.data.split('_')
    user_chat_id = int(user_chat_id)

    if action == 'verify':
        verify_product(user_chat_id, call)
    elif action == 'reject':
        reject_product(user_chat_id, call)

def verify_product(chat_id, call):
    product = products.get(chat_id)
    if product:
        category = product['category']
        phone = product['phone']
        price = float(call.message.reply_markup.inline_keyboard[0][0].callback_data.split('_')[1])  # Extract price
        increment_percentage = select_price_increment(call)  # Get the increment percentage from admins

        # Calculate final price
        final_price = price * (1 + increment_percentage / 100)

        # Send message to public channel
        bot.send_message(channel_id, f"🛒 New Product Available!\n"
                                      f"Category: {category}\n"
                                      f"Price: {final_price} (Original: {price})\n"
                                      f"Contact: {phone}")
        bot.edit_message_caption(
            caption="Verified ✅",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        bot.answer_callback_query(call.id, "Product verified!")

def reject_product(chat_id, call):
    bot.send_message(chat_id, "Sorry, your product could not be verified by the admins.")
    bot.edit_message_caption(
        caption="Rejected ❌",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )
    bot.answer_callback_query(call.id, "Product rejected.")

def select_price_increment(call):
    # Logic for admin to select the price increment (you can customize this part)
    # For now, let's assume a fixed increment for demonstration purposes
    return 250  # Replace with dynamic selection logic

@bot.message_handler(func=lambda message: True)
def handle_non_command(message):
    reply = (
        "I'm here to assist with your buying and selling needs!\n"
        "Please use one of the following commands:\n\n"
        "/start - Start the bot and learn more\n"
        "/sell - Start the selling process\n"
        "/help - List all available commands"
    )
    bot.reply_to(message, reply)

# Start the bot polling
if __name__ == '__main__':
    bot.polling()
