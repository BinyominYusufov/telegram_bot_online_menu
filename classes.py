import psycopg2

conn = psycopg2.connect(
        dbname='online_store_db',
        user='postgres',
        password='admin2009',
        host='localhost',
        port='5432'
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT,
    password VARCHAR(50),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute( """
CREATE TABLE IF NOT EXISTS dishes (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    price NUMERIC(10, 2),
    image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")



cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    dish_id INTEGER REFERENCES dishes(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def save(self):
        cursor.execute(
            'INSERT INTO users (password, username) VALUES (%s, %s)',
            (self.password, self.username)
        )
        conn.commit()

    @staticmethod
    def get(username, password):
        cursor.execute(
            'SELECT * FROM users WHERE username = %s AND password = %s',
            (username, password)
        )
        return cursor.fetchone()
    


class Dishes:
    def __init__(self, name, description, price, image):
        self.name = name
        self.description = description
        self.price = price
        self.image = image

    async def save(self):
        cursor.execute(
            """
            INSERT INTO dishes (name, description, price, image)
            VALUES (%s, %s, %s, %s)
            """,
            (self.name, self.description, self.price, self.image)
        )
        conn.commit()

    @staticmethod
    async def get_all():
        cursor.execute("SELECT * FROM dishes")
        data = cursor.fetchall()
        return data

    @staticmethod
    async def get_by_id(dish_id):
        cursor.execute("SELECT * FROM dishes WHERE id = %s", (dish_id,))
        data = cursor.fetchone()
        return data
    
    @staticmethod
    async def create(name, description, price, image):
        try:
            cursor.execute(
                "INSERT INTO dishes (name, description, price, image) VALUES (%s, %s, %s, %s) RETURNING id",
                (name, description, price, image)
            )
            conn.commit()
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error creating dish: {e}")
            return None
        

    @staticmethod
    async def delete(dish_id: int) -> bool:
        try:
            print(f"DEBUG: Deleting dish #{dish_id}")
            
            cursor.execute("DELETE FROM dishes WHERE id = %s", (dish_id,))
            conn.commit()
            
            cursor.execute("SELECT id FROM dishes WHERE id = %s", (dish_id,))
            if not cursor.fetchone():
                print(f"DEBUG: Dish #{dish_id} deleted successfully")
                return True
            else:
                print(f"DEBUG: Dish #{dish_id} still exists")
                return False
                
        except Exception as e:
            print(f"Error deleting dish: {e}")
            conn.rollback()
            return False

    @staticmethod
    def update(name, description, price, dish_id):
        cursor.execute(
            'UPDATE dishes SET name=%s, description=%s, price=%s WHERE id=%s',
            (name, description, price, dish_id)
        )
        conn.commit()


class Cart:
    @staticmethod
    def add_to_cart(user_id: int, dish_id: int) -> bool:
        try:
            cursor.execute('SELECT id FROM dishes WHERE id = %s', (dish_id,))
            if not cursor.fetchone():
                print(f"Dish {dish_id} not found")
                return False

            cursor.execute(
                "SELECT quantity FROM cart WHERE user_id=%s AND dish_id=%s", 
                (user_id, dish_id)
            )
            existing = cursor.fetchone()

            if existing:
                cursor.execute(
                    "UPDATE cart SET quantity = quantity + 1 WHERE user_id=%s AND dish_id=%s", 
                    (user_id, dish_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO cart (user_id, dish_id, quantity) VALUES (%s, %s, 1)", 
                    (user_id, dish_id)
                )

            conn.commit()
            return True

        except Exception as e:
            print(f"Error adding to cart: {e}")
            return False
        
    @staticmethod
    def get_cart(user_id):
        try:
            cursor.execute(
                """
                SELECT c.id, d.name, d.price, c.quantity
                FROM cart c
                JOIN dishes d ON c.dish_id = d.id
                WHERE c.user_id=%s
                """,
                (user_id,)
            )
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting cart: {e}")
            return []
    @staticmethod
    def remove_from_cart(cart_id: int) -> bool:
        try:
            cursor.execute('DELETE FROM cart WHERE id = %s', (cart_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing from cart: {e}")
            return False
    
    @staticmethod
    def clear_cart(user_id: int) -> bool:
        try:
            cursor.execute('DELETE FROM cart WHERE user_id = %s', (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error clearing cart: {e}")
            return False