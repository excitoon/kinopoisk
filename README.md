# База данных kinopoisk.ru

Репозиторий содержит скрипты для создания базы данных, парсер, написанный на Python и файлы, необходимые
для быстрого запуска парсера внутри Docker контейнера.

## Требования

Для запуска парсера необходимо:

* [Python 3](https://www.python.org/)
* Модули Python:
    * [psycopg2](initd.org/psycopg)
    * [lxml](lxml.de)
    * [requests](http://docs.python-requests.org/en/master/)
* [PostgreSQL](https://www.postgresql.org)
* [Docker](https://www.docker.com) и [docker-compose](https://docs.docker.com/compose/), если необходим запуск СУБД в контейнере

Работа парсера проверялась в ОС GNU/Linux, но поскольку Python кроссплатформенный язык, он также должен работать в Windows/MacOS.

## Конфигурация

Для конфигурации парсера необходимо использовать файл `config.py`. Параметры конфигурации описаны ниже.

Параметр|Комментарий
--------|-----------
dsn|Строка для подключения к базе данных, если используется Docker-контейнер на локальной машине, то это `postgresql://mdb@127.0.0.1:20000/mdb`
cache_path|Абсолютный путь к директории с кешем
year|Год, за который запускается парсер, используется для распаралелливания
anticaptcha['key']|Ключ к API сервиса anti-captcha.com
anticaptcha['url']|URL API сервиса anti-captcha.com, используется API версии 2 (https://api.anti-captcha.com/)

## База данных

Поднять базу данных для парсера можно одним из двух способов.

### База данных в Docker контейнере

Для того, чтобы поднять базу данных в Docker контейнере, достаточно запустить скрипт `rebuild.sh` либо отдельно следующие команды в корневой директории проекта:

```bash
docker build . -t mdb
docker-compose rm -f database
docker-compose up database
```

База данных будет доступна на порту 20000.

### Самостоятельная база данных

Для запуска СУБД вне Docker контейнера необходимо выполнить скрипт `db/install.sql` под супер пользователем БД. В psql при этом необходимо передать значение для SQL переменной `database`:

```bash
cd db
psql -v database=mdb -f install.sql
```

Этот скрипт создаст БД и все необходимые сущности в ней.