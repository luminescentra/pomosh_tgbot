import sqlite3
import logging
from telegram import ReplyKeyboardMarkup , ReplyKeyboardRemove , Update, InlineKeyboardMarkup , InlineKeyboardButton,Bot
from telegram.ext import Updater, CommandHandler , MessageHandler , Filters , ConversationHandler , CallbackQueryHandler, CallbackContext
import os
from telegram.utils.request import Request
from bot_pomosh.validators import validate_post_id
from datetime import datetime
from telegram import ParseMode
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

'''Иницализируем стартовую клавиатуру'''
START_BUTTON1_NEEDS_VIEW = 'start_button1'
START_BUTTON2_SHARES_VIEW = 'start_button2'
START_BUTTON3_ADD_POST = 'start_button3'
START_BUTTON_DELETE = 'start_button4'
START_BUTTON_INFO = 'start_button5'



def get_start_keyboard():
    inline_keyboard = [
        [InlineKeyboardButton( 'Cписок нуждающихся📋' , callback_data= START_BUTTON1_NEEDS_VIEW,),
        InlineKeyboardButton('Cписок готовых помочь📒', callback_data= START_BUTTON2_SHARES_VIEW)],
        [InlineKeyboardButton('Добавить пост✍️', callback_data=START_BUTTON3_ADD_POST)],
        [InlineKeyboardButton( 'Как работает бот❔', callback_data=START_BUTTON_INFO)],
    ]
    return InlineKeyboardMarkup(inline_keyboard )



WHAT , NAME , TAG, DESCRIPTION , NUMBER , СONFIRMATION=  range(6)
ID , CONFIRM = range(6, 8 )

def add_new_post(update : Update , context : CallbackContext):

    return WHAT

def what(update : Update , context : CallbackContext):
    # Получить вид поста
    query = update.callback_query
    data = query.data
    user_data = context.user_data
    user_data['type'] = data
    logger.info('type of post is %s', data)
    # Спросить имя
    update.effective_message.reply_text(
        "Ваш ответ принят&#9989;\nДля продолжения введите ваше имя:\n\n&#128071;&#128071;&#128071; ", parse_mode = ParseMode.HTML,
        reply_markup = ReplyKeyboardMarkup([[InlineKeyboardButton('Аноним' , callback_data='Аноним')]], resize_keyboard=True)
    )
    return NAME



def help_name(update : Update, context = CallbackContext):
    # Получить имя
    user = update.message.from_user
    user_data = context.user_data
    category = 'name'
    text = update.message.text
    user_data[category] = text
    logger.info('Name of  %s %s', user.first_name, update.message.text )
    # Спросить категорию поста
    inline_markup = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Препарат' , callback_data='medecine'),InlineKeyboardButton('Оборудование' , callback_data='equipment')],
            [InlineKeyboardButton('Услуга' , callback_data='kap'),InlineKeyboardButton('Очередь ( на рентген )' , callback_data='turn')],
            [InlineKeyboardButton('Другое', callback_data='another')],
        ]
    )
    update.message.reply_text(
        text = 'Ваш ответ принят!&#9989;', parse_mode = ParseMode.HTML,
        reply_markup = ReplyKeyboardRemove()
    )
    update.message.reply_text(
        "Теперь выберите категорию вашего поста.",
        reply_markup=inline_markup
    )
    return TAG

def help_tag(update:Update, context: CallbackContext):
    # Получить категорию
    query = update.callback_query
    user_data = context.user_data
    category = 'tag'
    data = update.callback_query.data
    if data == 'medecine':
        text = 'Препарат'
    elif data == 'equipment':
        text = 'Оборудование'
    elif data == 'kap':
        text = 'Услуга'
    elif data == 'turn':
        text = 'Очередь'
    elif data == 'another':
        text = 'Другое'
    user_data[category] = text
    logger.info('Tag of  %s' ,text)
    # Спросить описание публикации
    context.bot.send_message(
        chat_id=update.effective_message.chat_id,
        text = "Ваш ответ принят&#9989;\nТеперь введите ваше описание.\nПожалуйста вводите описание поста без ошибок и подробно.\n\n&#128071;&#128071;&#128071;", parse_mode=ParseMode.HTML
    )
    return DESCRIPTION

def help_description(update : Update , context : CallbackContext):
    # Получить описание
    user_data = context.user_data
    category = 'description'
    text = update.message.text
    user_data[category] = text
    logger.info('Description  %s', update.message.text)
    # Спросить контакты
    update.message.reply_text(
        "Принято&#9989;\nтеперь введите ваш номер телефона или способ связи с вами.\n\n&#128071;&#128071;&#128071;" , parse_mode = ParseMode.HTML
    )
    return NUMBER

def help_number(update : Update, context : CallbackContext):
    # Получить контакты
    user = update.message.from_user
    user_data = context.user_data
    category = 'number'
    text = update.message.text
    user_data[category] = text
    logger.info('Number of %s %s', user.first_name, update.message.text)
    # Спросить подтверждение
    markup = ReplyKeyboardMarkup(
        [
            [InlineKeyboardButton(text='Подтверждаю' , callback_data="confirm")],
            [InlineKeyboardButton(text ='Отмена' , callback_data='cancel')],
        ],
    )
    logger.info('Зафиксирована дата публикации %s' , str(datetime.now())[:10])
    user_data['date'] = str(datetime.now())[:10]
    update.message.reply_text(f'''Принято, ваша публикация готова&#128076;\nПроверьте и подтвердите её. Предварительный просмотр:\n
Ваше имя - {user_data['name']}\nКатегория - {user_data['tag']}\nОписание - {user_data['description']}\nКонтакты - {user_data['number']}\nДата публикации - {user_data['date']}''',
        reply_markup = markup, parse_mode = ParseMode.HTML
    )

    return СONFIRMATION
import random
def help_confirmation(update : Update , context : CallbackContext):
    # Получить подтверждение
    user_data = context.user_data
    user = update.message.from_user
    con = sqlite3.connect('Posts.sql')
    cursor = con.cursor()
    if update.message.text == 'Подтверждаю':
        logger.info("%s Confirmed form", user.first_name)

        # Добавление полученных данных в БД
        data = [user_data['name'] , user_data['tag'], user_data['description'], user_data['number'] , user_data['date']]
        post_id = random.randint(1000,10000)
        data.append(post_id)
        update.message.reply_text(
            "Ваша публикация подтверждена&#9989;\n\nИдентификационный номер вашей публикации - {}".format(post_id),
            reply_markup=ReplyKeyboardRemove(),
            parse_mode = ParseMode.HTML
        )
        if user_data['type'] == 'need_help':
            logger.info('Добавляю пост в таблицу нуждающихся')
            cursor.execute("INSERT into needs values ( ? , ? , ? , ? , ? , ?)", data)
            con.commit()
        elif user_data['type'] == 'share_help':
            logger.info('Добавляю пост в таблицу жертвующих')
            cursor.execute("INSERT into shares values ( ? , ? , ? , ? , ? , ?)", data)
            con.commit()
        logger.info("Публикация помещена в базу данных успешно")
    elif update.message.text == 'Отмена':
        logger.info("%s stoped to adding new post")
        update.message.reply_text(
        "Заполнение публикации прервано",
        reply_markup = ReplyKeyboardRemove()
    )
    else:
        return СONFIRMATION
    update.message.reply_text('Вернутся в главное меню?',reply_markup = back_keyboard)
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Отмена заполнения формы.',
                              reply_markup = back_keyboard)

    return ConversationHandler.END

back_keyboard = InlineKeyboardMarkup(
    inline_keyboard= [
        [InlineKeyboardButton('Назад ↩️',  callback_data='back')]#TODO смайлики во всех кнопках
    ]
)

def get_paginator_keyboard(page , max_pages, type ):
    keyboard = [
        [
            InlineKeyboardButton( '◀️Назад' , callback_data= f'back_page_{type}'),
            InlineKeyboardButton( f'{page}/{max_pages}' , callback_data= '_none'),
            InlineKeyboardButton( 'Вперед▶️' , callback_data= f'next_page_{type}'),
        ]
    ]
    keyboard.append([InlineKeyboardButton('Вернуться в главное меню↩️' , callback_data= 'back')])
    return InlineKeyboardMarkup(keyboard)


def needs_list_view(update  : Update , context : CallbackContext , type ):
    user_data = context.user_data
    page = user_data['page']
    try:
        for i in user_data['deletes']:
            context.bot.delete_message(update.effective_message.chat_id , i)
        user_data['deletes'] = []
    except:
        user_data['deletes'] = []
    if page < 1 :
        return
    end  = page* 6
    con = sqlite3.connect("Posts.sql")
    cursor = con.cursor()
    con.commit()
    cursor.execute(f'select * from {type}')
    if cursor.fetchall() == []:
        context.bot.send_message(chat_id= update.callback_query.message.chat_id ,
                                 text = "Публикациий пока нет :(",
                                 )
    list = []

    s = []
    for row in cursor.execute(f"select * from {type}"):
        for i in row[:5]:
            s.append(i)
        list.append('Имя: {}\nКатегория: {}\nОписание: {}\nСпособ связи: {}\n\nДата публикации {}'.format(s[0] , s[1] , s[2] , s[3] , s[4]))
        s = []
    max_pages = len(list) // 6
    if len(list) % 6 == 0:
        pass
    else:
        max_pages += 1
    if page > max_pages:
        return
    for i in range(end - 6 , end):
        try:
            if i == end -  1:
                user_data['deletes'].append(context.bot.send_message(chat_id=update.effective_message.chat_id, text=list[i] , reply_markup= get_paginator_keyboard(page , max_pages , type  )).message_id)
            else:
                user_data['deletes'].append(context.bot.send_message(chat_id=update.effective_message.chat_id ,text = list[i]).message_id)
        except IndexError:
            user_data['deletes'].append(context.bot.send_message(chat_id = update.effective_message.chat_id ,text  = 'Конец' ,reply_markup= get_paginator_keyboard(page, max_pages , type)).message_id)
            break
    print(user_data['deletes'])

def test(update : Update , context : CallbackContext):
    context.user_data['deletes'] = []
    chat_id = update.message.chat_id
    for i in range(10):
        context.user_data['deletes'].append(context.bot.send_message(chat_id = chat_id , text = 'Привет смотри 10 раз чето напишу').message_id)
        print(update.effective_message.chat_id)
    context.bot.send_message(chat_id = chat_id , text= "Удалить эти сообщения?" , reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Удалить' , callback_data= 'delete_test')]]) )


def do_start(update : Update, context : CallbackContext):
    context.bot.send_photo(chat_id=update.message.chat_id ,photo= 'https://imbt.ga/c3eYB0mjYC')
    context.bot.send_message(
        text = "Вас приветствует бот по помощи. Здесь вы можете поделится ею или найти её\nЧтобы продолжить выберите что нибудь:",
        chat_id= update.message.chat_id,
        reply_markup = get_start_keyboard()
    )



def do_help(update : Update , context : CallbackContext ):
    context.bot.send_message(chat_id= update.effective_message.chat_id, text = 'Здесь будет информация о боте' )
    context.bot.send_message(chat_id = update.effective_message.chat_id, text = 'Вернуться в главное меню?' ,  reply_markup = back_keyboard)


"""Инициализация диалога удаления"""

def delete_post(update: Update , context : CallbackContext ):
    context.bot.send_message(chat_id= update.effective_message.chat_id , text= 'Вы в меню удаления публикации.\n\nДля начала введите идентефикационный номер вашего поста, его вы получали после завершения добавлени помощи.\n\n&#128071;&#128071;&#128071;' , parse_mode=ParseMode.HTML)
    # спросить post_id пользователя
    return ID


def delete_id(update : Update , context : CallbackContext):
    # Получить post id
    post_id = update.message.text
    val = validate_post_id(post_id)
    if val:
        logger.info('post_id Прошел валидацию')
        context.user_data['post_id'] = post_id
        update.message.reply_text('Подтвердите удаление', reply_markup = ReplyKeyboardMarkup([[InlineKeyboardButton('Подтвердить' , callback_data='sdfdsf'), InlineKeyboardButton('Отмена' , callback_data= "льлвыалы")]]))
        return CONFIRM
    else:
        update.message.reply_text('Такого id не существует. Возможно вы ввели не правильно, попробуйте еще раз.')
        return ID


def delete_confirm(update: Update, context = CallbackContext):
    # Получить подтверждение
    answer = update.message.text
    if answer == 'Подтвердить':
        post_id = context.user_data["post_id"]
        logger.info('пользователь подтвердил удаление')
        con = sqlite3.connect('Posts.sql')
        cursor = con.cursor()
        cursor.execute("DELETE FROM shares WHERE post_id = {}".format(post_id))
        cursor.execute("DELETE FROM needs WHERE post_id = {}".format(post_id))
        con.commit()
        logger.info("Пост удален из базы данных")
        update.message.reply_text('Пост успешно удален из базы данных &#9989;, ваши данные полностью стерты с нашего сервера и не будут отображаться в наших списках.' , reply_markup = ReplyKeyboardRemove() ,parse_mode = ParseMode.HTML)
    elif answer == 'Отмена':
        logger.info('Пользователь прервал удаление')
        update.message.reply_text('Удаление поста отменено.', reply_markup= ReplyKeyboardRemove())
    update.message.reply_text('Вернуться в главное меню?' , reply_markup = back_keyboard)
    return ConversationHandler.END



def start_keyboard_handler(update: Update, context : CallbackContext ):
    chat_id = update.callback_query.message.chat.id
    query = update.callback_query
    data = query.data
    current_text = update.effective_message.text
    if data == START_BUTTON1_NEEDS_VIEW:
        query.edit_message_text(
            text = 'Показываю публикации людей нуждающихся в помощи',
        )
        context.user_data['page'] = 1
        return needs_list_view(update = update, context= context , type  = 'needs' )
    elif data == START_BUTTON2_SHARES_VIEW:
        query.edit_message_text(
            text = "Показываю публикации людей готовых помочь:"
        )
        context.user_data['page'] = 1
        return needs_list_view(update = update, context = context , type = 'shares')

    elif data == START_BUTTON3_ADD_POST:
        query.edit_message_text(text = 'Показываю меню добавления публикации')
        # Спросить вид поста
        context.bot.send_message(chat_id = chat_id,
            text = 'Для начала выберите, какая нужна публикация',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Мне нужна помощь', callback_data='need_help'),InlineKeyboardButton('Я готов помочь', callback_data='share_help')]])
        )

        return WHAT
    elif data == START_BUTTON_INFO:

        query.edit_message_text(text = "Здесь будет информация о боте  и как с ним работать" ,reply_markup= back_keyboard,  parse_mode=ParseMode.HTML)

    elif data == 'back':
        query.edit_message_text(text = "Главное меню\nЧтобы продолжить выберите что нибудь:" ,reply_markup=get_start_keyboard())
    elif data == 'next_page_needs':
        context.user_data['page'] += 1
        return needs_list_view(update = update , context = context , type = 'needs')
    elif data == 'next_page_shares':
        context.user_data['page'] += 1
        return needs_list_view(update = update , context = context , type = 'shares')
    elif data == 'back_page_needs':
        context.user_data['page'] -= 1
        return needs_list_view(update=update, context=context, type='needs')
    elif data == 'back_page_shares':
        context.user_data['page'] -= 1
        return needs_list_view(update=update, context=context, type='shares')
    elif data == 'delete_test':
        for i in context.user_data['deletes']:
            context.bot.delete_message(chat_id , i)


def main():
    bot = Bot(
        token = "1226045587:AAHQgOJ6e9mvH3jQPFwHaJBLVyOsGs2iPCU",
    )
    updater = Updater(
        bot = bot,
        use_context=True,
    )

    print(updater.bot.get_me())
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_keyboard_handler)],

        states = {
            WHAT : [CallbackQueryHandler(what , pass_user_data=True)],

            NAME : [MessageHandler(Filters.text , help_name , pass_user_data = True )],

            TAG : [CallbackQueryHandler(help_tag, pass_user_data=True )],

            DESCRIPTION : [MessageHandler(Filters.text, help_description ,  pass_user_data=True)],

            NUMBER : [MessageHandler(Filters.text , help_number ,pass_user_data = True )],

            СONFIRMATION : [MessageHandler(Filters.text,help_confirmation, pass_user_data=True), ],
        },
        fallbacks= [CommandHandler('cancel', cancel)]

    )
    delete_conv = ConversationHandler(
        entry_points= [CommandHandler('delete' , callback = delete_post)],
        states={
            ID : [MessageHandler(Filters.text , delete_id , pass_user_data=True)],
            CONFIRM : [MessageHandler(Filters.text , delete_confirm , pass_user_data=True)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    updater.dispatcher.add_handler(conv)
    updater.dispatcher.add_handler(delete_conv)
    updater.dispatcher.add_handler(CallbackQueryHandler( callback= start_keyboard_handler))
    updater.dispatcher.add_handler(CommandHandler('start' , callback = do_start))
    updater.dispatcher.add_handler(CommandHandler('help', callback=do_help))
    updater.dispatcher.add_handler(CommandHandler('test' , callback= test))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
