vk2irc
======
A bridge between chats in popular social network VK http://vk.com and arbitrary IRC server. Supports following modes:
- messages from VK chat room are delivered to IRC channel and backwards
- messages from VK chat room are delivered to IRC channel one way
- messages from IRC channel are delivered to VK chat room one way

Following types of attachements to VK chat messages are supported:
- photo, IRC message will contain URL to photo
- audio, IRC message will contain artist name, track title and URL to audio file
- video, IRC message will contain video title and URL to VK player
- wall post, IRC message will contain URL to wall post

Dependencies
------------
- IRC client library 8.9.1 https://pypi.python.org/pypi/irc
- VK API 5.23

Getting started
---------------
Copy file vk2irc.py somewhere on your drive and give it 755 permissions

    chmod 755 vk2irc.py

In the home folder of user that would be used to start application create config file and name it .vk2irc Example configuration is located in vk2irc.ini In section _[vk_bot]_, parameter _access_token_ is the token that could be obtained from VK API, details on the URL

 https://vk.com/dev/auth_mobile

Application would need the following access rights (parameter _scope_ in http request) _friends,photos,audio,video,messages,offline_

To be able to connect to VK multiuser chat room application needs to know it's id (_chat_id_). This value could be obtained in response to a following request to VK API (note: the request must be executed from behalf of user that owns VK application and who's name would be used to deliver IRC messages to VK multiuser dialog)

 https://vk.com/dev/messages.getDialogs

Section _[irc_bot]_ contains IRC server settings. Details under this URL

 https://pypi.python.org/pypi/irc

Execute the following command to start application

    ./vk2irc.py >> ~/vk2irc.log 2>&1 &

Execute the following command to stop it

    ./pkill -f vk2irc

vk2irc
======
Мост между диалогами из популярной социальной сети ВКонтакте http://vkontakte.ru и произвольным IRC сервером. Поддерживает следующие режимы работы:
- сообщения из многопользовательского диалога ВКонтакте доставляются в IRC канал и обратно
- сообщения из многопользовательского диалога ВКонтакте доставляются в одном направлении в IRC канал
- сообщения из IRC канала доставляются в одном направлении в многопользовательский диалог ВКонтакте

Поддерживаются следующие типы вложений для сообщений из диалогов ВКонтакте:
- фото, IRC сообщение будет содержать ссылку на фото
- аудио, IRC сообщение будет содержать название исполнителя, название композиции и ссылку на аудиофайл
- видео, IRC сообщение будет содержать навание видео и ссылку на плеер ВКонтакте
- запись на стене, IRC сообщение будет содержать ссылку на запись на стене

Зависимости
-----------
- клиенская библиотека IRC версии 8.9.1 https://pypi.python.org/pypi/irc
- VK API 5.23

Установка и запуск
------------------
Скопируйте файл vk2irc.py в любое удобное для вас место и сделайте его исполнимым

    chmod 755 vk2irc.py

В домашней папке пользователя из под котого вы будете запускать приложение создайте конфигурационный файл .vk2irc Пример конфигурации можно посмотреть в файле vk2irc.ini В секции _[vk_bot]_ необходимо указать _access_token_, подробнее о получении _access_token_ можно прочитать по ссылке

 https://vk.com/dev/auth_mobile

Для работы приложению необходимы следующие права доступа (параметр _scope_) _friends,photos,audio,video,messages,offline_

Для подключения к многопользовательскому диалогу ВКонтакте необходимо указать его идентификатор (_chat_id_), это значение можно получить сделав следующий вызов VK API из под пользователя под которым будет зарегистрировано приложение и от лица которого планируется вести беседу в многопользовательском диалоге ВКонтакте

 https://vk.com/dev/messages.getDialogs
 
В секции _[irc_bot]_ указываются настройки для подключения к IRC серверу. Подробнее см. 

 https://pypi.python.org/pypi/irc
 
Для запуска приложения выполните следующую команду

    ./vk2irc.py >> ~/vk2irc.log 2>&1 &
    
Для остановки приложения

    ./pkill -f vk2irc

