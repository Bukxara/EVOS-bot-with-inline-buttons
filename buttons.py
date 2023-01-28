from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from main import db

contact = ReplyKeyboardMarkup(
	keyboard = [
		[
			KeyboardButton(text = "Press this button to send your phone number", request_contact = True)
		], 
	], resize_keyboard = True
)

location = ReplyKeyboardMarkup(
	keyboard = [
		[
			KeyboardButton(text = "Press this button to send your location", request_location = True)
		], 
	], resize_keyboard = True
)

menu = ReplyKeyboardMarkup(
	keyboard = [
		[
			KeyboardButton(text = "🍽 Order")
		],
		[
			KeyboardButton(text = "⚙️ Settings"),
			KeyboardButton(text = "📞 Support")
		],
		[
			KeyboardButton(text = f"📥 Basket")
		]
	], resize_keyboard = True
)

async def get_all_category():
	data = db.select_all_category()
	categories = InlineKeyboardMarkup(row_width = 2)
	for category in data:
		callback_data = category[0]
		button_text = category[1]
		categories.insert(
			InlineKeyboardButton(text = button_text, callback_data = f"categories_{callback_data}"))
	categories.add( 
		InlineKeyboardButton(text = "⬅️Back", callback_data = "back1"))
	return categories

async def get_products_by_id(id, tg_id = None):
	data = db.select_products_by_id(id)
	products = InlineKeyboardMarkup(row_width = 2)
	for product in data:
		callback_data = product[0]
		button_text = product[2]
		products.insert(
			InlineKeyboardButton(text = button_text, callback_data = f"products_{callback_data}"))
	basket = db.select_all_basket(tg_id)
	if basket:
		products.add(InlineKeyboardButton(text = "📥 Basket", callback_data = "basket"))
	products.add(InlineKeyboardButton(text = "⬅️Back", callback_data = "back2"))
	return products

# async def get_quant(value = 1):
# 	quantity = InlineKeyboardMarkup(row_width = 3)
# 	quantity.insert(
# 		InlineKeyboardButton(text = "-", callback_data = "decrease"))
# 	quantity.insert(
# 		InlineKeyboardButton(text = value, callback_data = "quantity"))
# 	quantity.insert(
# 		InlineKeyboardButton(text = "+", callback_data = "increase"))
# 	quantity.add(InlineKeyboardButton(text = "📥 Add to basket", callback_data = "purchase"))
# 	return quantity

# sub_menu = ReplyKeyboardMarkup(
# 	keyboard = [
# 		[
# 			KeyboardButton(text = "📥 Basket")
# 		],
# 		[
# 			KeyboardButton(text = "⬅️Back"),
# 		]
# 	], resize_keyboard = True
# )

async def get_quantity(product_id):
	quantity = InlineKeyboardMarkup(row_width = 3)
	for i in range(1,10):
		quantity.insert(
			InlineKeyboardButton(text = i, callback_data = f"quantity_{product_id}/{i}"))
	quantity.add(InlineKeyboardButton(text = "⬅️Back", callback_data = f"back3_{product_id}"))
	return quantity

async def see_basket(tg_id):
	data = db.select_all_basket(tg_id)
	basket = InlineKeyboardMarkup(row_width = 2)
	basket.insert(
		InlineKeyboardButton(text = "⬅️Back", callback_data = "back2"))
	basket.insert(
		InlineKeyboardButton(text = "🚖Order", callback_data = "order"))
	basket.insert(
		InlineKeyboardButton(text = "🗑Empty the basket", callback_data = "empty"))
	for product in data:
		name = db.get_category_by_product_id(product[1])[2]
		basket.add(
		InlineKeyboardButton(text = f"❌{name}", callback_data = f"delete_{product[0]}"))
	return basket	