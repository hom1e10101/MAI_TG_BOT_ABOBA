# NAS run 0 v kode


## Состав команды:

1. **Фокина Татьяна** - _Team Lead & Analyst & Miro Maps Designer & Presentation Editor_
2. **Балдынов Тамир** - _Backend Developer_
3. **Меньшиков Алексей** - _Based Backend Developer_
4. **Кучин Клим** - _Presentation Designer_

---

## Описание проекта:

## Функционал
  
* 🕒 **История мест:** Пользователь может просматривать места, в которых уже побывал
  
* 🔎 **Выбор мест по запросу:** Гибкая система выбора мест, котрая в зависимости от желаемого места или действия (фиксированных, например “Прогулка”, “Театр”, “Музей”, “Ресторан” и т.д) в формате команд выдаёт список мест
  
* ℹ️ **Информация о месте:** Пользователь может получить информацю и краткую сводку о положительных и отрицательных комментариях о месте, которое он выбрал сам или ему порекомендовал ассистент. Также информация автоматически добавляется из групп в tg
  
* ⭐ **Рейтинг мест:** Места отсортированы по рейтингу пользователей от лучшего к худшему
  
* 💬 **Комментарии:** Пользователь может оставлять комментарии о посещенном месте
  
* 🗣 **Естественное общение:** Использованые YandexGPT делает общение с ассистентом более естественное
  
* 🗺️ **Карта:** Интеграция с API карт для мгновенного отображения места на карте
  
* 👑 **Ролевая модель:** Модель "Администратор > manager > пользователь" устанавливает четкую иерархию. Это позволяет более эффективно защитить пользователей от ложной информации о месте или непозволительных комментариев


## Технологический стек:
<a href="https://www.python.org/"><img src="https://img1.akspic.ru/attachments/originals/4/9/3/3/6/163394-programmist_na_python-piton-algoritmicheskij_yazyk-stoyanie-ishodnyj_kod-3840x2160.png" width="66" height="40"></a><a href="https://ya.ru/ai/gpt"><img src="https://static.tengrinews.kz/userdata/news/2023/news_519361/thumb_b/photo_454258.jpeg" width="80" height="40"></a><a href="https://yandex.cloud/ru"><img src="https://avatars.mds.yandex.net/i?id=add1f7dbe58abc3233026125fc749956_l-9107575-images-thumbs&n=13" width="70" height="40"></a>


## Запуск проекта:
1. Установить необходимые библиотеки с помощью [requirments.txt](requirements.txt) написав в терминале ```pip install -r requirements.txt```
2. Убедиться в наличии или установить sqlite3
3. Создать файл secret.py в папке bot и вписать ключи:
```
tg_api = '<апи ключ получаемый в Botfather>'
database = r'<полный путь к базе данных>'
yandex_url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
yandex_api = 'уникальный апи ключ получаемый в яндекс клауд'
```

## Ссылки на ресурсы:
<a href="https://ru.yougile.com/board/6t8fc2a2cdbi">
  <img src="https://play-lh.googleusercontent.com/z8qX6XNHOIRaXjXotyuPKLgekAa1XZ-8ny34CpbUKoFl8-GT2kXZFM-dVAj8VCVxCw" width="22" height="22"></a> Ссылка на Yougile: https://ru.yougile.com/board/6t8fc2a2cdbi ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ<a href="https://miro.com/app/board/uXjVIFSljUY=/?share_link_id=849545594885"><img src="https://ugc.production.linktr.ee/dbe645a3-9c9a-432c-8629-8674ad649964_c77dc9c2-a0c6-41ab-9e54-265339f5339c-og-image.png?io=true&size=thumbnail-stack-v1_0" width="22" height="22"></a> Ссылка на Miro: https://miro.com/app/board/uXjVIFSljUY=/?share_link_id=849545594885

## Демонстрация нашего проекта:
[Бот](https://t.me/New_places_fr_bot)ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ
[Презентация](https://docs.google.com/presentation/d/1ghj36Nk9g4GOQpQQGlNKV6goC4h20Wu8bk1N6nlqaf4/edit?slide=id.p1#slide=id.p1)
## Платформы, где представлены наши результаты:
<img src="https://github.com/user-attachments/assets/6b9f41e3-1749-46b2-be42-5e672eb6da24" width="220" height="230">ㅤㅤㅤㅤㅤ<img src="https://github.com/user-attachments/assets/26ea43e5-605e-46fa-bf08-c9007b8bbe03" width="220" height="230">
