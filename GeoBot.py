from aiogram import Bot, Dispatcher, types, F
from aiogram.dispatcher.router import Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, PollAnswer,CallbackQuery, FSInputFile, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
import asyncio
import tempfile
import nest_asyncio
import matplotlib.pyplot as plt
import io
import json
import logging

nest_asyncio.apply()

API_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
ADMIN_PASSWORD = "xxxxxxxxxxxxxxxxx"


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
web_info = WebAppInfo(url="https://uladzislaup.github.io/")


keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Mapa", web_app=web_info)]
    ],
    resize_keyboard=True
    )

questions = [
    {"question": "1.Jakie funkcje użytkowe powinny dominować na Placu Defilad?", 
     "options": ["Strefy rekreacyjne (parki, place zabaw)",
                 "Strefy handlowo-usługowe (sklepy, kawiarnie)",
                 "Strefy kulturalne (muzea, galerie)"]},
    {"question": "2.Jakie rozwiązania transportowe preferujesz na Placu Defilad?",
     "options": ["Więcej ścieżek rowerowych",
                 "Rozbudowa infrastruktury dla pieszych",
                 "Zwiększenie dostępności parkingów"]},
    {"question": "3.Jakie elementy zieleni miejskiej są dla Ciebie najważniejsze na Placu Defilad?",
     "options": ["Duże trawniki i otwarte przestrzenie",
                 "Klomby kwiatowe i małe ogrody",
                 "Drzewa i zadrzewienia"]},
    {"question": "4.Jakie działania kulturalne powinny być organizowane na Placu Defilad?",
     "options": ["Festiwale i koncerty plenerowe",
                 "Wystawy i instalacje artystyczne",
                 "Pokazy filmowe i teatry uliczne"]},
    {"question": "5.Jakie udogodnienia powinny być dostępne na Placu Defilad?",
     "options": ["Więcej ławek i miejsc do siedzenia",
                 "Więcej fontann i punktów wodnych",
                 "Więcej miejsc do piknikowania"]},
    {"question": "6.Jakie działania proekologiczne powinny być wdrożone na Placu Defilad?",
     "options": ["Systemy zbierania i recyklingu odpadów",
                 "Instalacje z energią odnawialną",
                 "Ogrody deszczowe i systemy zarządzania wodą opadową"]},
    {"question": "7.Jakie typy oświetlenia preferujesz na Placu Defilad?",
     "options": ["Energooszczędne lampy LED",
                 "Lampy solarne",
                 "Tradycyjne latarnie miejskie"]},
    {"question": "8.Jakie udogodnienia dla dzieci powinny być na Placu Defilad?",
     "options": ["Place zabaw z różnymi atrakcjami",
                 "Strefy edukacyjne i interaktywne",
                 "Mini park linowy"]},
    {"question": "9.Jakie działania społeczne powinny być wspierane na Placu Defilad?",
     "options": ["Warsztaty i zajęcia edukacyjne",
                 "Spotkania i inicjatywy sąsiedzkie",
                 "Projekty artystyczne z udziałem mieszkańców"]},
    {"question": "10.Jakie elementy małej architektury są dla Ciebie najważniejsze na Placu Defilad?",
     "options": ["Nowoczesne i funkcjonalne wiaty przystankowe",
                 "Estetyczne i wygodne ławki",
                 "Stylowe kosze na śmieci i stojaki na rowery"]}
]

webapp_questions = [
    "Czy nowo powstały budynek Muzeum Sztuki Nowoczesnej spełnia Państwa oczekiwania estetyczne i funkcjonalne?",
    "Czy likwidacja tunelu pod Marszałkowską wpłynie na Państwa codzienne poruszanie się po mieście i ogólną estetykę tej części Warszawy?",
    "Czy odkrycie historycznych elementów infrastruktury, takich jak bruk i tory starych ulic, podczas przebudowy placu Defilad powinno wpłynąć na zmianę planów rewitalizacji tego obszaru?",
    "Czy podobają się Państwu dotychczasowe zmiany wprowadzone na Placu Defilad, polegające na zastąpieniu betonu zielenią?",
    "Czy uważają Państwo, że zwykły parking naziemny powinien zostać zlikwidowany na rzecz dodatkowej przestrzeni publicznej lub zieleni, przy jednoczesnym zachowaniu parkingu podziemnego?",
    "Czy popierają Państwo koncepcję, która zakłada wyrównanie terenu Placu Defilad do poziomu Parku Świętokrzyskiego i ul. Marszałkowskiej?"
]

user_data = {}
admin_data = {}
poll_results = {i: [0, 0, 0] for i in range(len(questions))}
webapp_results = {i: {'yes': 0, 'no': 0} for i in range(6)}

def has_participated_in_surveys(user_id):
    participated_in_poll = user_id in user_data and user_data[user_id]['question_index'] == len(questions)
    participated_in_webapp = any(result['yes'] + result['no'] > 0 for result in webapp_results.values())
    return participated_in_poll, participated_in_webapp

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    file = FSInputFile('start.png')
    button1 = types.InlineKeyboardButton(text='Ankieta', callback_data='ankieta')
    kd = types.InlineKeyboardMarkup(inline_keyboard=[[button1]])
    welcome_message = (
        "Witamy w naszym bocie! \n\n"
        "Bot został zaprojektowany jako narzędzie wspierające proces partycypacyjnego projektowania przestrzeni miejskich. "
        "Jego głównym celem jest zbieranie opinii i propozycji mieszkańców dotyczących elementów i funkcji przestrzennych. Dzięki analizie zgromadzonych danych, aplikacja umożliwia lepsze zrozumienie "
        "potrzeb mieszkańców, co z kolei pozwala na formułowanie rekomendacji do planowania i projektowania przestrzeni miejskich.\n\n"
        "Bot oferuje dwie formy ankiet:\n"
        "1. **Zwykła Ankieta** - klasyczna forma zbierania opinii. Aby wziąć udział, kliknij przycisk „Ankieta” pod tą wiadomością.\n"
        "2. **Ankieta Mapowa** - ankieta z mapą, na której zaznaczone są obszary objęte opracowaniem. Pytania dotyczą już "
        "wprowadzonych lub wprowadzanych zmian na tych obszarach. Aby wziąć udział w ankiecie mapowej, kliknij przycisk „Mapa” znajdujący się "
        "po lewej stronie pola do wprowadzania tekstu.\n\n"
        "Zachęcamy do udziału w obu ankietach oraz do przeglądania podsumowań opinii innych użytkowników."
    )
    await message.answer_photo(photo=file, caption=welcome_message, reply_markup=kd)
    
@router.message(F.text == "/stat")
async def cmd_stat(message: Message):
    chat_id = message.chat.id
    participated_in_poll, participated_in_webapp = has_participated_in_surveys(chat_id)

    if participated_in_poll or participated_in_webapp:
        buttons = []
        if participated_in_poll:
            buttons.append(types.InlineKeyboardButton(text="Statystyki Ankiety", callback_data="poll_stats"))
        if participated_in_webapp:
            buttons.append(types.InlineKeyboardButton(text="Statystyki Ankiety Mapowej", callback_data="webapp_stats"))
        
        markup = types.InlineKeyboardMarkup(inline_keyboard=[buttons])
        await message.answer("Wybierz statystyki do przeglądania:", reply_markup=markup)
    else:
        button1 = types.InlineKeyboardButton(text='Ankieta', callback_data='ankieta')
        button2 = types.InlineKeyboardButton(text='Mapa', web_app=web_info)
        kd = types.InlineKeyboardMarkup(inline_keyboard=[[button1, button2]])
        await message.answer("Najpierw weź udział w ankietach, aby zobaczyć statystyki.", reply_markup=kd)
        
@router.message(F.text == "/stat_admin")
async def cmd_stat_admin(message: Message):
    await message.answer("Proszę podać hasło:")
    admin_data[message.chat.id] = {'awaiting_password': True}

@router.message(F.text)
async def handle_admin_password(message: Message):
    chat_id = message.chat.id
    if chat_id in admin_data and admin_data[chat_id].get('awaiting_password'):
        if message.text == ADMIN_PASSWORD:
            total_users = len(user_data)
            users_completed_poll = sum(1 for u in user_data.values() if u['question_index'] == len(questions))
            users_completed_webapp = sum(
                1 for user_id in user_data
                if any(webapp_results[i]['yes'] + webapp_results[i]['no'] > 0 for i in range(len(webapp_questions)))
            )
            
            response = (
                f"Liczba osób, które uruchomiły bota: {total_users}\n"
                f"Liczba osób, które przeszły ankietę: {users_completed_poll}\n"
                f"Liczba osób, które przeszły ankietę mapową: {users_completed_webapp}"
            )
            await message.answer(response)
        else:
            await message.answer("Niepoprawne hasło.")
        admin_data.pop(chat_id, None)
    else:
        await handle_unknown_message(message)


@router.callback_query(F.data == "poll_stats")
async def poll_stats(call: CallbackQuery):
    await send_stat_buttons(call.message.chat.id)

@router.callback_query(F.data == "webapp_stats")
async def webapp_stats(call: CallbackQuery):
    await send_webapp_stat_buttons(call.message.chat.id)

@router.callback_query(lambda call: call.data == 'ankieta')
async def start_survey(call: CallbackQuery):
    chat_id = call.message.chat.id
    participated_in_poll, participated_in_webapp = has_participated_in_surveys(chat_id)

    if participated_in_poll and participated_in_webapp:
        await call.message.answer("Już wypełniłeś obie ankiety. Możesz zobaczyć statystyki za pomocą /stat.")
    elif participated_in_poll:
        await call.message.answer("Już wypełniłeś zwykłą ankietę. Możesz przystąpić do ankiety mapowej lub zobaczyć statystyki za pomocą /stat.")
        await bot.send_message(chat_id, "Wypełnij ankietę mapową:", reply_markup=keyboard)
    else:
        user_data[chat_id] = {'question_index': 0, 'answered_questions': set(), 'active_poll': None}
        await send_next_question(chat_id)

async def send_next_question(chat_id):
    index = user_data[chat_id]['question_index']
    if index < len(questions):
        question = questions[index]
        poll_message = await bot.send_poll(
            chat_id,
            question=question["question"],
            options=question["options"],
            is_anonymous=False,
            type='regular',
            allows_multiple_answers=False
        )
        user_data[chat_id]['active_poll'] = poll_message.poll.id
    else:
        await send_stat_buttons(chat_id)
        await bot.send_message(chat_id, "Dziękujemy za udział w ankiecie! Zachęcamy do wzięcia udziału również w naszej ankiecie mapowej!", reply_markup=keyboard)  # Potem wyślij wiadomość tekstową

@router.poll_answer()
async def handle_poll_answer(poll_answer: PollAnswer):
    chat_id = poll_answer.user.id
    question_index = user_data[chat_id]['question_index']

    if chat_id in user_data:
        if poll_answer.poll_id == user_data[chat_id]['active_poll']:
            poll_results[question_index][poll_answer.option_ids[0]] += 1
            user_data[chat_id]['answered_questions'].add(question_index)
            user_data[chat_id]['question_index'] += 1
            await send_next_question(chat_id)
        else:
            await bot.send_message(chat_id, "Pod uwagę jest brana tylko pierwsza udzielona odpowiedź, cofnięcie nie zmienia wyniku.")
            
async def send_stat_buttons(chat_id):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    buttons = []
    for i, question in enumerate(questions):
        buttons.append(types.InlineKeyboardButton(text=f"Pytanie {i+1}", callback_data=f"stats_{i}"))
    markup.inline_keyboard.extend([buttons[i:i+2] for i in range(0, len(buttons), 2)])
    file = FSInputFile('ankiet.png')
    await bot.send_photo(chat_id, file, caption="Wybierz pytanie, aby zobaczyć statystyki ankiety w postaci diagramu kołowego:", reply_markup=markup)

async def send_webapp_stat_buttons(chat_id):
    markup = types.InlineKeyboardMarkup(inline_keyboard=[])
    buttons = []
    for i in range(6):
        buttons.append(types.InlineKeyboardButton(text=f"Pytanie WebApp {i+1}", callback_data=f"webapp_stats_{i}"))
    markup.inline_keyboard.extend([buttons[i:i+3] for i in range(0, len(buttons), 3)])

    await bot.send_message(chat_id, "Wybierz pytanie, aby zobaczyć statystyki ankiety mapowej w postaci diagramu kołowego:", reply_markup=markup)
    
    
@router.callback_query(F.data.startswith('stats_'))
async def send_pie_chart(call: types.CallbackQuery):
    question_index = int(call.data.split('_')[1])
    question = questions[question_index]
    labels = question["options"]
    sizes = poll_results[question_index]

    if sum(sizes) == 0:
        await call.message.answer("Brak danych do wyświetlenia wykresu dla tego pytania.")
        return
    filtered_labels = [label if size > 0 else '' for label, size in zip(labels, sizes)]
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct=lambda p: f'{p:.1f}%' if p > 0 else '', startangle=90)
    ax.axis('equal') 
    plt.title(f'Pytanie {question_index + 1}', pad=20)
    ax.legend(wedges, labels, loc="upper left", bbox_to_anchor=(-0.1, -0.15), frameon=False)
    plt.subplots_adjust(bottom=0.3)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        plt.savefig(tmpfile.name)
        tmpfile.seek(0)
        plt.close(fig)
        file = FSInputFile(tmpfile.name)
        await call.message.answer_photo(file)
    

@router.callback_query(F.data.startswith('webapp_stats_'))
async def send_webapp_pie_chart(call: types.CallbackQuery):
    question_index = int(call.data.split('_')[2])
    question = webapp_questions[question_index]
    labels = ["Tak", "Nie"]
    sizes = [webapp_results[question_index]['yes'], webapp_results[question_index]['no']]

    if sum(sizes) == 0:
        await call.message.answer("Brak danych do wyświetlenia wykresu dla tego pytania.")
        return
    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(sizes, labels=None, autopct=lambda p: f'{p:.1f}%' if p > 0 else '', startangle=90)
    ax.axis('equal')
    plt.title(f'Pytanie {question_index + 1}', pad=20)
    ax.legend(wedges, labels, loc="upper left", bbox_to_anchor=(-0.1, -0.15), frameon=False)
    plt.subplots_adjust(bottom=0.3)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        plt.savefig(tmpfile.name)
        tmpfile.seek(0)
        plt.close(fig)
        file = FSInputFile(tmpfile.name)
        await call.message.answer_photo(file)
        
@router.message(F.content_type == "web_app_data")
async def handle_webapp_data(message: types.Message):
    try:
        logging.info("Odebrano web_app_data")
        data = json.loads(message.web_app_data.data)
        print(data)
        print(webapp_results)
        for key, answer in data.items():
            button_id = int(key.replace('question', '')) - 1
            if answer == 'yes':
                webapp_results[button_id]['yes'] += 1
            elif answer == 'no':
                webapp_results[button_id]['no'] += 1

        logging.info(f"Zaktualizowane webapp_results: {webapp_results}")
        if all(result['yes'] + result['no'] > 0 for result in webapp_results.values()):
            await send_webapp_stat_buttons(message.chat.id)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        await message.answer("Wystąpił błąd podczas przetwarzania odpowiedzi.")
        
@router.message(F.content_type == types.ContentType.TEXT)
async def handle_unknown_message(message: types.Message):
    response_text = (
        "Cześć! Nie rozumiem, co powiedziałeś. Możesz wziąć udział w naszych ankietach, wpisując /start. "
        "Jeśli już uczestniczyłeś, wpisz /stat ponownie, aby sprawdzić wyniki, które aktualizują się na żywo."
    )
    file = FSInputFile('och.png')
    await message.answer_photo(photo=file, caption=response_text)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())