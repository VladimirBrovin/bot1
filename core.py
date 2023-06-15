from datetime import datetime 
import vk_api

from config import acces_token



class VkTools():
    def __init__(self, acces_token):
       self.api = vk_api.VkApi(token=acces_token)
       self.offset = 0

    def get_profile_info(self, user_id):
        """Получаем данные по id"""
        info = self.api.method('users.get',
                               {'user_id': user_id,
                               'fields': 'city,bdate,sex,relation'})
        if info:
            info = info[0]
            user_info = {'name': f'{info.get("first_name")} {info.get("last_name")}',
                         'id':  info['id'],
                         'age': datetime.now().year - int(info['bdate'].split('.')[-1]) if 'bdate' in info else None,
                         'sex': info['sex'],
                         'city': info['city']['title'] if 'city' in info else None,
                         'relation': info['relation'] if 'relation' in info else 0
                        }
            return user_info
    
    def serch_users(self, params):
        """Поиск анкет по параметрам"""
        sex = 1 if params['sex'] == 2 else 2
        hometown = params['city']
        age_from = params['age'] - 5
        age_to = params['age'] + 5
        status = params['relation']

        users = self.api.method('users.search',
                                {'count': 10,
                                 'offset': self.offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'hometown': hometown,
                                 'status': status,
                                 'is_closed': False,
                                 'has_photo': 1,
                                })
        self.offset += 10
        result = []
        try:
            users = users['items']
            for user in users:
                if user['is_closed'] == False:
                    result.append({'id': user['id'],
                                   'name': user['first_name'] + ' ' + user['last_name']})
        except KeyError:
            ...
        return result
    

    def get_photos(self, user_id):
        """Получаем ссамые популярные фото"""
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                 }
                                )
        result = []
        try:
            photos = photos['items']
            for photo in photos:
                result.append({'owner_id': photo['owner_id'],
                            'id': photo['id'],
                            'likes': photo['likes']['count'],
                            'comments': photo['comments']['count'],
                            }
                            )
            
            result.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)
        
        except KeyError:
            ...
        return result[:3]


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(789657038)
    # print(params)
    users = bot.serch_users(params)
    for u in users:
        print(u)
    print(bot.get_photos(users[-1]['id']))

