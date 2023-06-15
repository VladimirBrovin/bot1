# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from data_store import DataBase
from core import VkTools
from dialog import *

class BotInterface():

    

    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.api = VkTools(acces_token=acces_token)
        self.params = None
        self.db = DataBase()
        self.worksheets = []
        self.flag = None

    def message_send(self, user_id, message, attachment=None):
        """срабатывание бота"""
        self.interface.method('messages.send',
                                {'user_id': user_id,
                                'message': message,
                                'attachment': attachment,
                                'random_id': get_random_id()})
        
    def profile_get(self):
        """проверка анкеты"""
        while True:
            if self.worksheets:
                worksheet = self.worksheets.pop()
                if self.db.from_bd(self.params['id'], worksheet['id']) == False:
                    return worksheet
            else:
                self.worksheets = self.api.serch_users(self.params)
                if self.worksheets == None:
                    return self.worksheets
        
    def event_handler(self):
        longpoll = VkLongPoll(self.interface)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                attach = None
                if self.flag == None and command:
                    self.flag = 'start'
                    self.params = self.api.get_profile_info(event.user_id)
                    message = ('Привет, я бот-VKinder\nМогу помочь с поиском партнера\n'
                               'Начнём?')
                
                elif command in NEGATIVE:
                    message = (f'До скорых встреч {self.params["name"]}')
                    self.flag = None
                    self.params = None

                elif self.flag == 'start':
                    if command in POSITIVE:
                        if (self.params['age'] == None or 
                            self.params['city'] == None):
                            message = (f'Ваши параметры\n'
                                       f'город: {self.params["city"]}\n'
                                       f'возраст: {self.params["age"]}\n'
                                       f'требуют уточнения!')
                            self.flag = 'change'
                        message = (f'Хорошо, {self.params["name"]}\n'
                                   f'ищем анкету по вашим данным\n'
                                   f'город: {self.params["city"]}\n'
                                   f'возраст: {self.params["age"]}\n'
                                   f'при необходимости корректировки'
                                   f'наберите "корректировка/изменить"\n'
                                   f'"поиск" для начала')
                    
                    elif command == 'поиск' or command == 'gjbcr':
                        self.flag = 'insearch'
                        message = ('пишите "далее" либо "f" для продолжения\n'
                                   '"закончить" либо "q" для завершения поиска')
                    
                    elif command in CORRECT:
                        self.flag = 'change'
                        message = 'наберите "город" либо "возраст для изменения'

                    else:
                        message = 'я вас не понимаю'

                elif self.flag == 'insearch':
                    if command == 'f' or command == 'а':
                        profile = self.profile_get()
                        if profile:
                            message = f'{profile["name"]} vk.com/id{profile["id"]}'
                            self.db.to_bd(self.params['id'], profile['id'])
                            attach = ''
                            for photo in self.api.get_photos(profile['id']):
                                attach += f'photo{photo["owner_id"]}_{photo["id"]},'
                        else:
                            message = 'Ничего не нашли, попробуйте заменить данные'

                elif self.flag == 'change':
                    if command in CITY:
                        message = 'введите город'
                        self.flag = 'city'
                    if command in AGE:
                        message = 'введите возраст'
                        self.flag = 'age'

                elif self.flag == 'city':
                    if command.isdigit():
                        message = f'город введен не корректно'
                    else:
                        self.params['city'] = command.capitalize()
                        message = f'город изменен на {self.params["city"]}\nПродолжим?'
                        self.flag = 'start'

                elif self.flag == 'age':
                    if command.isdigit():
                        self.params['age'] = int(command)
                        message = f'возраст изменен на {self.params["age"]}\nПродолжим?'
                        self.flag = 'start'
                    else:
                        message = f'возраст введен не корректно'

                self.message_send(event.user_id, message=message, attachment=attach)

if __name__ == '__main__':
    bot = BotInterface(comunity_token, acces_token)
    bot.event_handler()
