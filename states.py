from aiogram.dispatcher.filters.state import State, StatesGroup

class UserData(StatesGroup):
	name = State()
	contact = State()
	location = State()

class ProductData(StatesGroup):
	product_id = State()
	product_photo = State()