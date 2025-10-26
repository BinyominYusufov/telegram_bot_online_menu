from aiogram import Bot ,Dispatcher ,types,F
from aiogram.filters import Command
from aiogram.types import KeyboardButton,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup,ReplyKeyboardRemove
from aiogram.fsm.state import State,StatesGroup


bot=Bot(token='7894244421:AAH03S31csYHMefRt3oVFNS1Ej-VTkYnHB8')
dp=Dispatcher()
 


lgn = KeyboardButton(text='/login')
rgstr = KeyboardButton(text='/register')

auth = ReplyKeyboardMarkup(keyboard=[[lgn,rgstr]],resize_keyboard=True)


add = KeyboardButton(text='/add')
show = KeyboardButton(text='/show')
logout = KeyboardButton(text='/logout')

admin_menu = ReplyKeyboardMarkup(keyboard=[[add,show],[logout]],resize_keyboard=True)


show_cart = KeyboardButton(text='/show_cart')
show_products = KeyboardButton(text='/show_products')

user_menu = ReplyKeyboardMarkup(keyboard=[[show_cart,show_products],[logout]],resize_keyboard=True)



class Register(StatesGroup):
    username=State()
    password=State()


class Login(StatesGroup):
    username=State()
    password=State()


class Product(StatesGroup):
    name=State()
    description=State()
    price=State()
    image=State()


class UpdateProduct(StatesGroup):
    name = State()
    description = State()
    price = State()