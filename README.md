README к проектной работе по курсу "Python Developer: Basic":
- Описание проекта
- Структура проекта
- Ансибл


Описание проекта:
- Проект представляет собой начальный мониторинг серверов бизнес-задачи, на которых еще (по разным причинам) не запущена централизованная система мониторинга.
- Все проверки специфичны именно для этой бизнес-задачи.
- При совпадении условий проверок (ошибок) отправляется сообщение в телеграм  и/или консоль (message\\_type)
- Сам мониторинг запускается через linux (systemd) как системный сервис
- Предусмотрена возможность фиксации интервала времени, в течении которого будут отправляться сообщения.
- Отправка сообщений выполнена в виде базового шаблона с возможностью добавления комментариев.
- Предусмотрено, что в случае ошибки, не будет "спама", только разовая отправка, т.е. после получение сообщения нужно подключиться и проверить работоспособность сервисов.
- Часть ошибок имеют накопительный эффект, т.к. проверки зависят от работы внешней и внутренней сети (+1 к кол-ву при ошибке, =0 при 
положительной проверке)
- При достижении статуса "явной ошибки", в основном словаре происходит переключение конкретной проверки c True на False.
- В процессе работы мониторинга в логах всегда можно посмотреть статус каждой проверки (False / True) в виде JSON.
- В рамках работы по курсу проект мониторинга был незначительно адаптирован (от реального расположения на серверах) под возможность демонстрации.
- Работоспособность проверена под Python3 11/12/13




Структура проекта:
- main.py - основной запускаемый модуль
- functions.py - все функции проверок и часть (непосредственно нужных для проверок) переменных.
- global\\_vars.py - все основные переменные
- HOSTNAME.py - шаблон имени, меняется через Ansible при установке
- config.yaml - конфиг для одной из проверок (atto\\_socket)
- ips.txt - список адресов для одной из проверок (терминалы)
- monitoring.service - сервис для запуска мониторинга
- version.py - файл для контроля версий
- requirements.txt - выгрузка модулей для pip
- MOK (api\\_mok.py, socket\\_mok.py) - заглушки для базовой проверки работоспособности


Ансибл:
- Разворачивание происходит через ансибл-плейбуки (можно предоставить при необходимости)

Порядок запуска:
- Скачать проект
- Установить зависимости
- Задать переменные в случае необходимости
- Запустить МОКи при необходимости
- Запустить проект через main.py

