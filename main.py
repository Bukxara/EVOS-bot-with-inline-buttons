import logging
from config import API_TOKEN, admin
from aiogram import Bot, Dispatcher, executor, types
from sqlite import Database
from buttons import *
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from states import UserData, ProductData
from aiogram.dispatcher.filters import Text

#TOKEN AND ADMIN FILES ARE LOCATED IN config.py FILE

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())
db = Database()
db.create_users()


@dp.message_handler(commands='start', state = "*")
async def send_welcome(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    username = message.from_user.username
    data = db.select_user(tg_id)
    if data is None:
        await message.reply("Welcome to EVOS! Please, enter your name!")
        db.insert_user(tg_id, username)
        await state.set_state(UserData.name)
    else:
        await message.answer("Hi there!", reply_markup = menu)

@dp.message_handler(state = UserData.name)
async def send_welcome(message: types.Message, state: FSMContext):
    if not message.text.isalpha():
        await message.reply("Please send a valid name! e.g. Hardwell")
        return
    await state.update_data(name = message.text)
    await message.answer("Will you share your phone number, please?", reply_markup = contact)
    await state.set_state(UserData.contact)

@dp.message_handler(content_types='contact', state = UserData.contact)
async def send_welcome(message: types.Message, state: FSMContext):
    await state.update_data(contact = message.contact.phone_number)
    await message.answer("Enter your location", reply_markup = location)
    await state.set_state(UserData.location)

@dp.message_handler(content_types='location', state = UserData.location)
async def send_welcome(message: types.Message, state: FSMContext):
    await state.update_data(location = (message.location.latitude, message.location.longitude))
    tg_id = message.from_user.id
    data = await state.get_data()
    name_ = data.get("name")
    contact_ = data.get("contact")
    location_ = data.get("location")
    db.update_user(tg_id, name_, contact_, location_)
    count = db.count_users()
    username = message.from_user.username
    await message.answer("You've successfully signed up!", reply_markup = menu)
    await bot.send_message(admin, f"@{username} has just signed up!: Now you have {count[0]} users!")
    await state.finish()
    await state.reset_state()


@dp.message_handler(text = "🍽 Order")
async def start_menu(message: types.Message):
    categories = await get_all_category()
    await message.answer("Select the category", reply_markup = categories)


@dp.callback_query_handler(Text(startswith = "categories_"))
async def show_products(call: types.CallbackQuery):
    tg_id = call.from_user.id
    idx = call.data.index("_")
    product_id = call.data[idx+1:]
    products = await get_products_by_id(product_id, tg_id)
    await call.message.answer_photo(photo = open(f"images/{product_id}.jpg", "rb"), reply_markup = products)


@dp.callback_query_handler(text = "back1")
async def start_menu(call: types.CallbackQuery):
    categories = await get_all_category()
    await call.message.answer("Hi there!", reply_markup = menu)


@dp.callback_query_handler(Text(startswith = "products_"))
async def show_products(call: types.CallbackQuery):
    idx = call.data.index("_")
    product_id = call.data[idx+1:]
    product = db.get_category_by_product_id(product_id)
    quantity = await get_quantity(product_id)
    await call.message.answer_photo(photo = product[3], caption = f"Price: {product[4]} sum\n\nHow many?", reply_markup = quantity)


@dp.callback_query_handler(Text(startswith = "quantity_"))
async def show_products(call: types.CallbackQuery):
    tg_id = call.from_user.id
    idx = call.data.index("_")
    product_idx = call.data.index("/")
    product_id = call.data[idx+1:product_idx]
    count = call.data[product_idx+1:]
    data = db.select_basket(product_id, tg_id)
    if data is None:
        db.insert_basket(product_id, tg_id, count)
        await call.answer("Product has been added!")
    else:
        db.update_bakset(product_id, tg_id, count)
        await call.answer("Your basket has been updated!")
    product = db.get_category_by_product_id(product_id)
    back = await get_products_by_id(product[1], tg_id)
    await call.message.answer_photo(photo = open(f"images/{product[1]}.jpg", "rb"), reply_markup = back)
    

@dp.callback_query_handler(Text(startswith = "back3_"))
async def show_products(call: types.CallbackQuery):
    tg_id = call.from_user.id
    idx = call.data.index("_")
    product_id = call.data[idx+1:]
    product = db.get_category_by_product_id(product_id)
    back = await get_products_by_id(product[1], tg_id)
    await call.message.answer_photo(photo = open(f"images/{product[1]}.jpg", "rb"), reply_markup = back)


@dp.callback_query_handler(text = "back2")
async def start_menu(call: types.CallbackQuery):
    categories = await get_all_category()
    await call.message.answer("Select the category", reply_markup = categories)


@dp.message_handler(text = "⬅️Back")
async def start_menu(message: types.Message):
    categories = await get_all_category()
    await message.answer("Select the category", reply_markup = categories)

@dp.callback_query_handler(text = "basket")
async def empty_basket(call: types.CallbackQuery):
    tg_id = call.from_user.id
    data = db.select_all_basket(tg_id)
    if not data:
        await call.message.answer("Your basket is empty!")
    else:
        numbers = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣"}
        total_price = 0
        text = "In basket:\n"
        for product in data:
            name = f"{db.get_category_by_product_id(product[1])[2]}\n"
            price = db.get_category_by_product_id(product[1])[-1]
            text += f"{(numbers.get(product[-1]))} ✖ {name}"
            total_price += int(price.replace(' ', ''))*int(product[-1])
        markup = await see_basket(tg_id)
        await call.message.answer(f"{text}\nProducts: {total_price}\nDelivery: 10 000 sum\nTotal: {total_price+10000}", reply_markup = markup)

@dp.message_handler(text = "📥 Basket")
async def start_menu(message: types.Message):
    tg_id = message.from_user.id
    data = db.select_all_basket(tg_id)
    if not data:
        await message.answer("Your basket is empty!")
    else:
        numbers = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣"}
        total_price = 0
        text = "In basket:\n"
        for product in data:
            name = f"{db.get_category_by_product_id(product[1])[2]}\n"
            price = db.get_category_by_product_id(product[1])[-1]
            text += f"{(numbers.get(product[-1]))} ✖ {name}"
            total_price += int(price.replace(' ', ''))*int(product[-1])
        markup = await see_basket(tg_id)
        await message.answer(f"{text}\nProducts: {total_price}\nDelivery: 10 000 sum\nTotal: {total_price+10000}", reply_markup = markup)


@dp.callback_query_handler(Text(startswith = "delete_"))
async def show_products(call: types.CallbackQuery):
    tg_id = call.from_user.id
    idx = call.data.index("_")
    product_id = call.data[idx+1:]
    db.delete_basket(product_id, tg_id)
    await call.answer("Your basket has been updated!")
    data = db.select_all_basket(tg_id)
    if not data:
        await call.message.delete()
        await call.message.answer("Your basket is empty!")
    else:
        total_price = 0
        text = "In basket:\n"
        for product in data:
            name = f"{db.get_category_by_product_id(product[1])[2]}\n"
            price = db.get_category_by_product_id(product[1])[-1]
            text += f"{str(product[-1])} ✖ {name}"
            total_price += int(price.replace(' ', ''))*int(product[-1])
        markup = await see_basket(tg_id)
        await call.message.edit_text(f"{text}\nProducts: {total_price}\nDelivery: 10 000 sum\nTotal: {total_price+10000}")
        await call.message.edit_reply_markup(markup)

@dp.callback_query_handler(text = "empty")
async def empty_basket(call: types.CallbackQuery):
    tg_id = call.from_user.id
    db.empty_basket(tg_id)
    await call.answer("Your basket is now empty!")
    await call.message.delete()
    categories = await get_all_category()
    await call.message.answer("Select the category", reply_markup = categories)

@dp.callback_query_handler(text = "order")
async def order_the_order(call: types.CallbackQuery):
    tg_id = call.from_user.id
    user = db.select_user(tg_id)
    basket = db.select_all_basket(tg_id)
    total_price = 0
    text = f"The order has been initiated:\nName: {user[2]}, Username: @{user[1]}Contact: {user[3]}\n"
    for product in basket:
        name = f"{db.get_category_by_product_id(product[1])[2]}\n"
        price = db.get_category_by_product_id(product[1])[-1]
        text += f"{str(product[-1])} ✖ {name}"
        total_price += int(price.replace(' ', ''))*int(product[-1])
    await call.message.delete()
    await call.message.answer("Thank you for ordering with EVOS!\nSoon you will be contacted by one of our admins!", 
        reply_markup = menu)
    await bot.send_message(admin, f"{text}Total: {total_price+10000}")
    db.empty_basket(tg_id)
    location = user[4].replace(" ", "").replace("(", "").replace(")", "")
    latitude, longitude = location.split(",")
    await bot.send_location(admin, 
        latitude = float(latitude), longitude = float(longitude))


@dp.message_handler(text = "📞 Support")
async def start_menu(message: types.Message):
    tg_id = message.from_user.id
    user = db.select_user(tg_id)
    await message.reply("Soon you will be contacted by one of our admins!")
    await bot.send_message(admin, 
        f"{user[2]} would like you to contact them via {user[3]}")

@dp.message_handler(text = "⚙️ Settings")
async def start_menu(message: types.Message):
    await message.answer("Loading. . .")


@dp.message_handler(commands='update', state = "*", user_id = admin)
async def update_photo(message: types.Message, state: FSMContext):
    await message.reply("Please enter the id of the product")
    await state.set_state(ProductData.product_id)


@dp.message_handler(state = ProductData.product_id)
async def update_photo(message: types.Message, state: FSMContext):
    await state.update_data(product_id = message.text)
    await message.reply("Please send the photo of the product")
    await state.set_state(ProductData.product_photo)


@dp.message_handler(content_types = "any", state = ProductData.product_photo)
async def update_photo(message: types.Message, state: FSMContext):
    await state.update_data(product_photo = message.photo[-1]["file_id"])
    data = await state.get_data()
    product_id_ = data.get("product_id")
    product_photo_ = data.get("product_photo")
    db.update_photo(product_id_, product_photo_)
    await message.reply("You've successfully uploaded the photo for the product!")
    await state.finish()
    await state.reset_state()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)