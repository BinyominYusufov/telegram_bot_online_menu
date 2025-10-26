from states import dp,types,bot,Command,auth,Register,Login,admin_menu,user_menu, Product,UpdateProduct
from classes import User,Dishes,Cart
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram import F

sessions ={}

@dp.message(Command('start'))
async def start(message:types.Message):
    await message.answer('''🌟 Welcome to Our Bot! 🌟\n\nHello, dear user! We're thrilled to have you here. 🎉\n\nPlease choose an option to continue:''',reply_markup=auth)
    


@dp.message(Command('register'))
async def register(message:types.Message,state:FSMContext):
   await message.answer(
        "🌟 *Welcome to registration!* 🌟\n\n"
        "Please enter your *username*:",
        parse_mode="Markdown"
    )
   await state.set_state(Register.username)

@dp.message(Register.username)
async def get_username(message:types.Message,state:FSMContext):
    try:
        await state.update_data(username=message.text)
        await state.set_state(Register.password)
        await message.answer(
            "🔒 *Great! Now enter your password:*",
            parse_mode="Markdown"
        )
    except Exception:
        await message.answer(
            "😔 *Error processing username. Please try again.*",
            parse_mode="Markdown"
        )

@dp.message(Register.password)
async def get_password(message: types.Message, state: FSMContext):
    try:
        await state.update_data(password=message.text)
        data = await state.get_data()
        user = User(data['username'], data['password'])
        await user.save()
        await message.answer(
            "🎉 *Registration successful!* 🎉\n\n"
            f"Welcome, *{data['username']}*! Use /login to sign in.",
            parse_mode="Markdown"
        )
        await state.clear()
    except Exception:
        await message.answer(
            "😔 *Error during registration. User may already exist. Please try again.*",
            parse_mode="Markdown"
        )


@dp.message(Command('login'))
async def login(message:types.Message,state:FSMContext):
   await message.answer(
        "🔐 *Welcome to login!* 🔐\n\n"
        "Please enter your *username*:",
        parse_mode="Markdown"
    )
   await state.set_state(Login.username)

@dp.message(Login.username)
async def get_username(message:types.Message,state:FSMContext):
    try:
        await state.update_data(username=message.text)
        await state.set_state(Login.password)
        await message.answer(
            "🔒 *Now enter your password:*",
            parse_mode="Markdown"
        )
    except Exception:
        await message.answer(
            "😔 *Error processing username. Please try again.*",
            parse_mode="Markdown"
        )

@dp.message(Login.password)
async def get_password(message: types.Message, state: FSMContext):
    try:
        await state.update_data(password=message.text)
        data = await state.get_data()

        user = User.get(data['username'], data['password'])

        sessions[message.from_user.id] = {
            'username': data['username'],
            'is_admin': user[3]
        }

        if user:
            if user[3]:
                await message.answer(
                    "👑 *Admin access granted!* 👑",
                    parse_mode="Markdown",
                    reply_markup=admin_menu
                )
            else:
                await message.answer(
                    "🎉 *Login successful!* 🎉",
                    parse_mode="Markdown",
                    reply_markup=user_menu
                )
        else:
            await message.answer("User not found! 🤦‍♀️🤔")

    except Exception as e:
        print(f"Error: {e}")
        await message.answer("An error occurred. Please try again.")
    finally:
        await state.clear()

@dp.message(F.text == '/logout')
async def logout(message: types.Message, state: FSMContext):
    await state.clear() 
    await message.answer(
        "👋 You logged out successfully! 👋\n\n",
        reply_markup=types.ReplyKeyboardRemove() 
    )

    await message.answer(
        "Please choose an option to continue: 👇",
        reply_markup=auth  
    )


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@dp.message(Command('show'))
async def show_dishes(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in sessions:
        await message.answer("⚠️ You are not logged in. Please use /login first.")
        return

    if not sessions[user_id].get('is_admin'):
        await message.answer("🚫 You are not authorized to use this command.")
        return

    try:
        dishes = await Dishes.get_all()

        if not dishes:
            await message.answer("🍽️ No dishes found in the database.")
            return
        for dish in dishes:
            text = f"🍴 *{dish[1]}* — {dish[3]} somoni\n📖 {dish[2]}"
            buttons = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✏️ Update", callback_data=f"update_{dish[0]}"),
                    InlineKeyboardButton(text="🗑️ Delete", callback_data=f"delete_{dish[0]}")
                ]
            ])

            await message.answer(text, parse_mode="Markdown", reply_markup=buttons)

    except Exception as e:
        print(f"Error: {e}")
        await message.answer("❌ An error occurred while loading dishes.")


@dp.message(Command('show_products'))
async def show_dishes(message: types.Message):
    user_id = message.from_user.id

    if user_id not in sessions:
        await message.answer("⚠️ You are not logged in. Please use /login first.")
        return

    try:
        dishes = await Dishes.get_all()

        if not dishes:
            await message.answer("🍽️ No dishes found in the database.")
            return

        for dish in dishes:
            text = f"🍴 *{dish[1]}* — {dish[3]} somoni\n📖 {dish[2]}"

            button = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🛒 Add to Cart", callback_data=f"add_{dish[0]}"),
                ]
            ])
            await message.answer(text, parse_mode="Markdown", reply_markup=button)

    except Exception as e:
        print(f"Error: {e}")
        await message.answer("❌ An error occurred while loading dishes.")



@dp.message(Command('add'))
async def add_product(message: types.Message, state: FSMContext):
    try:
        user_id = message.from_user.id

        if user_id not in sessions:
            await message.answer('⚠️ Please login first using /login')
            return
            
        if not sessions[user_id].get('is_admin'):
            await message.answer('❌ Access denied. Admin only!')
            return
        
        await message.answer('🍴 Enter dish name:')
        await state.set_state(Product.name)
         
    except Exception as e:
        print(f"Error in add_product: {e}")
        await message.answer('❌ Error starting product addition')

@dp.message(Product.name)
async def get_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('📝 Enter dish description:')
    await state.set_state(Product.description)

@dp.message(Product.description)
async def get_product_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('💰 Enter dish price (in somoni):')
    await state.set_state(Product.price)

@dp.message(Product.price)
async def get_product_price(message: types.Message, state: FSMContext):
    try:

        price = float(message.text)
        if price <= 0:
            await message.answer('❌ Price must be positive. Enter price again:')
            return
            
        await state.update_data(price=price)
        await message.answer('🖼️ Send image for the dish (or send "skip" to continue without image):')
        await state.set_state(Product.image)
        
    except ValueError:
        await message.answer('❌ Please enter a valid number for price:')
        return

@dp.message(Product.image)
async def get_product_image(message: types.Message, state: FSMContext):
    try:
        product_data = await state.get_data()
        
        image_url = None
        if message.photo:

            photo = message.photo[-1]

            image_url = photo.file_id
        elif message.text and message.text.lower() == 'skip':
            image_url = None
        else:
            await message.answer('❌ Please send an image or "skip"')
            return

        dish = await Dishes.create(
            name=product_data['name'],
            description=product_data['description'],
            price=product_data['price'],
            image=image_url
        )
        
        await message.answer(f'✅ Dish "{product_data["name"]}" added successfully!',reply_markup=admin_menu)
        await state.clear()
        
    except Exception as e:
        print(f"Error saving product: {e}")
        await message.answer('❌ Error saving dish to database')
        await state.clear()

@dp.callback_query(lambda c: c.data and c.data.startswith('delete_'))
async def delete_dish_callback(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        
        if user_id not in sessions or not sessions[user_id].get('is_admin'):
            await callback.answer("❌ Access denied. Admin only!", show_alert=True)
            return
            
        dish_id = int(callback.data.split('_')[1])
        
        success = await Dishes.delete(dish_id)
        
        if success:
            await callback.message.delete()
            await callback.answer("✅ Dish deleted successfully!", show_alert=True)
        else:
            await callback.answer("❌ Failed to delete dish", show_alert=True)
        
    except Exception as e:
        print(f"Error in delete_dish_callback: {e}")
        await callback.answer("❌ Error deleting dish", show_alert=True)


@dp.callback_query(lambda c: c.data and c.data.startswith('update_'))
async def update_dish_callback(callback: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        
        if user_id not in sessions or not sessions[user_id].get('is_admin'):
            await callback.answer("❌ Access denied. Admin only!", show_alert=True)
            return
            
        dish_id = int(callback.data.split('_')[1])
        
        await state.update_data(dish_id=dish_id)
        await callback.message.answer("📝 Enter new name:")
        await state.set_state(UpdateProduct.name)
        await callback.answer()
        
    except Exception as e:
        print(f"Error in update_dish_callback: {e}")
        await callback.answer("❌ Error", show_alert=True)


@dp.message(UpdateProduct.name)
async def update_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📄 Enter new description:")
    await state.set_state(UpdateProduct.description)

@dp.message(UpdateProduct.description)
async def update_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("💰 Enter new price:")
    await state.set_state(UpdateProduct.price)

@dp.message(UpdateProduct.price)
async def update_price(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        dish_id = data['dish_id']
        name = data['name']
        description = data['description']
        price = float(message.text)
        
        Dishes.update(name, description, price, dish_id)
        
        await message.answer(f"✅ Dish #{dish_id} updated successfully!", reply_markup=admin_menu)
        await state.clear()
        
    except ValueError:
        await message.answer('❌ Please enter a valid number for price:')
    except Exception as e:
        print(f"Error updating dish: {e}")
        await message.answer("❌ Error updating dish", reply_markup=admin_menu)
        await state.clear()



@dp.callback_query(lambda c: c.data and c.data.startswith('add_'))
async def add_to_cart_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    dish_id = int(callback.data.split('_')[1])

    success = Cart.add_to_cart(user_id, dish_id)  # Вызываем напрямую из класса
    if success:
        await callback.answer(f"✅ Dish added to cart!", show_alert=True)
    else:
        await callback.answer("❌ Error adding dish to cart.", show_alert=True)

@dp.message(Command('show_cart'))
async def show_cart_user(message: types.Message):
    user_id = message.from_user.id

    if user_id not in sessions:
        await message.answer("⚠️ You are not logged in. Please use /login first.")
        return

    items = Cart.get_cart(user_id) 
    if not items:
        await message.answer("🛒 Your cart is empty!")
        return

    text = "🛒 *Your Cart:*\n\n"
    total = 0
    
    keyboard = []
    
    for item in items:
        cart_id, name, price, quantity = item
        total += price * quantity
        text += f"🍴 {name} — {price} somoni x {quantity}\n"
        
        keyboard.append([
            types.InlineKeyboardButton(
                text=f"🗑️ Remove {name}", 
                callback_data=f"remove_from_cart_{cart_id}"
            )
        ])

    text += f"\n💰 Total: {total} somoni"
    
    keyboard.append([
        types.InlineKeyboardButton(
            text="🧹 Clear All Cart", 
            callback_data="clear_cart"
        )
    ])
    
    reply_markup = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer(text, parse_mode="Markdown", reply_markup=reply_markup)




@dp.callback_query(lambda c: c.data and c.data.startswith('remove_from_cart_'))
async def remove_from_cart_callback(callback: types.CallbackQuery):
    try:
        cart_id = int(callback.data.split('_')[3])
        
        success = Cart.remove_from_cart(cart_id)
        
        if success:
            await callback.message.edit_text("✅ Item removed from cart!")
        else:
            await callback.answer("❌ Error removing item", show_alert=True)
            
    except Exception as e:
        print(f"Error in remove_from_cart_callback: {e}")
        await callback.answer("❌ Error", show_alert=True)

@dp.callback_query(lambda c: c.data == "clear_cart")
async def clear_cart_callback(callback: types.CallbackQuery):
    try:
        user_id = callback.from_user.id
        
        success = Cart.clear_cart(user_id)
        
        if success:
            await callback.message.edit_text("🧹 Cart cleared!")
        else:
            await callback.answer("❌ Error clearing cart", show_alert=True)
            
    except Exception as e:
        print(f"Error in clear_cart_callback: {e}")
        await callback.answer("❌ Error", show_alert=True)

if __name__ == '__main__':
    dp.run_polling(bot)
    