import sqlite3

class Database:

	def __init__(self):
		self.conn = sqlite3.connect("Bot.db")
		self.c = self.conn.cursor()

	def create_users(self):
		self.c.execute("""CREATE TABLE IF NOT EXISTS Users(
				id PRIMARY KEY AUTOINCREMENT,
				telegram_id varchar(20),
				username varchar(25),
				name varchar(50) NULL,
				contact varchar(15) NULL,
				location varchar(30) NULL
				)""")

	def insert_user(self, tg_id, username):
		self.c.execute("INSERT INTO Users (telegram_id, username) VALUES (?, ?)", (tg_id, username))
		return self.conn.commit()

	def select_user(self, tg_id):
		self.c.execute("SELECT * FROM Users WHERE telegram_id = ?", (tg_id,))
		return self.c.fetchone()

	def count_users(self):
		self.c.execute("SELECT COUNT(*) FROM Users")
		return self.c.fetchone()

	def update_user(self, tg_id, name, ph_num, location):
		self.c.execute(f"""UPDATE Users SET name = "{name}", contact = "{ph_num}", location = "{location}" 
			WHERE telegram_id = "{tg_id}" """)
		return self.conn.commit()


	def create_category(self):
		self.c.execute("""CREATE TABLE IF NOT EXISTS categories(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			category_name varchar(30)
			)""")

	def insert_category(self, name):
		self.c.execute("INSERT INTO categories (category_name) VALUES (:name) ", {"name": name})
		return self.conn.commit()

	def select_all_category(self):
		self.c.execute("SELECT * FROM categories")
		return self.c.fetchall()

	
	def create_products(self):
		self.c.execute("""CREATE TABLE IF NOT EXISTS Products(
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			category_id INTEGER,
			product_name varchar(50),
			product_photo TEXT NULL,
			product_price varchar(20),
			FOREIGN KEY (category_id) REFERENCES categories(id) 
			)""")

	def insert_product(self, ctg_id: int, name, price):
		self.c.execute("""INSERT INTO Products (category_id, product_name, product_price) 
			VALUES (:id, :name, :price)""", {"id": ctg_id, "name": name, "price": price})
		return self.conn.commit()

	def select_products_by_id(self, id):
		self.c.execute("SELECT * FROM Products WHERE category_id = ?", (id,))
		return self.c.fetchall()

	def get_category_by_product_id(self, id):
		self.c.execute("SELECT * FROM Products WHERE id = ?", (id, ))
		return self.c.fetchone()

	def update_photo(self, id, photo):
		self.c.execute(f"""UPDATE Products SET (product_photo) = ("{photo}") WHERE id = "{id}" """)
		return self.conn.commit()

	def create_basket(self):
		self.c.execute("""CREATE TABLE IF NOT EXISTS Basket (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			products_id INTEGER,
			tg_id varchar(30),
			count INTEGER
			)""")

	def select_basket(self, id, tg_id):
		self.c.execute("SELECT * FROM Basket WHERE products_id = ? AND tg_id = ?", (id, tg_id))
		return self.c.fetchone()

	def insert_basket(self, product_id, tg_id, count):
		self.c.execute("INSERT INTO Basket (products_id, tg_id, count) VALUES (?, ?, ?)", 
			(product_id, tg_id, count))
		return self.conn.commit()

	def update_bakset(self, product_id, tg_id, count):
		self.c.execute("UPDATE Basket SET products_id = ?, count = ? WHERE tg_id = ?", (product_id, count, tg_id))
		return self.conn.commit()

	def select_all_basket(self, tg_id):
		self.c.execute("SELECT * FROM Basket WHERE tg_id = ?", (tg_id,))
		return self.c.fetchall()

	def delete_basket(self, product_id, tg_id):
		self.c.execute("DELETE FROM Basket WHERE id = ? AND tg_id = ?", (product_id, tg_id))
		return self.conn.commit()

	def empty_basket(self, tg_id):
		self.c.execute("DELETE FROM Basket WHERE tg_id = ?", (tg_id, ))
		return self.conn.commit()