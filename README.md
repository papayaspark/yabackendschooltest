# backendschooltest
Данный репозиторий содержит исходный код REST API, являющегося результатом выполнения второго задания для поступления в школу бэкенд-разработки Яндекса.


### Инструкции по развертыванию проекта

1. __Обновить систему и установить необходимые для работы пакеты.__

    ```
    sudo apt update && sudo apt upgrade
    sudo apt install build-essential libssl-dev python3-dev python3-venv
    ```
    
2. __Установить MySQL Server 8.0.__

    *2.1. Скачать deb-пакет с официального сайта MySQL.*

    ```
    wget -c https://dev.mysql.com/get/mysql-apt-config_0.8.13-1_all.deb
    ```
    
    *2.2. Сконфигурировать репозиторий MySQL. Оставить настройки по умолчанию.*
    
    ```
    sudo dpkg -i mysql-apt-config_0.8.13-1_all.deb
    ```
    
    *2.3. Установить непосредственно саму СУБД и сопутствующие библиотеки.*
    
    ```
    sudo apt install mysql-server libmysqlclient-dev
    ```
        
3. __Загрузить файлы проекта из репозитория.__

   ```
   git clone https://github.com/greenasruby/backendschooltest
   ```
    
4. __Создать виртуальное окружение в папке проекта и установить нужные пакеты из requirements.txt.__
    
   ```
   cd backendschooltest
   python3 -m venv backendschoolvenv
   source backendschoolvenv/bin/activate
   pip install -r requirements.txt
   ```

5. __Создать необходимые базы и пользователя в MySQL.__
    ```
   cd backendschooltest
   mysql -u root -p < ./scripts/database_setup.sql
    ``` 
    
6. __Выполнить миграции и запустить проект.__
    ```
    cd backendschooltest/citizensapi
    ./manage.py migrate
    ./manage.py runserver 0.0.0.0:8080
    ```
   Если все сделано правильно, то по адресу 0.0.0.0:8080 будет доступен наш сервер. Затем нужно выйти при помощи `Ctrl + C`.
   
7. __Установить gunicorn__.

    Установка 
    
    ```
    pip install gunicorn
   ```
    
   Проверка работоспособности
   
   ```
   gunicorn citizensapi.wsgi:application --bind 0.0.0.0:8080
   ```

8. Создать скрипт для автоматического запуска gunicorn c API. 

    ```
    cd backendschooltest
    touch ./backendschoolvenv/bin/gunicorn_start
    ```
   
    В созданный файл gunicorn_start добавить следующее.
    
    ```
    #!/bin/bash

    NAME="citizens_api"                                     # Name of the application
    DJANGODIR=~/backendschooltest/citizens_api              # Django project directory
    SOCKFILE=~/backendschooltest/run/gunicorn.sock          # we will communicte using this unix socket
    USER=entrant                                            # the user to run as
    GROUP=sudo                                              # the group to run as
    NUM_WORKERS=3                                           # how many worker processes should Gunicorn spawn
    DJANGO_SETTINGS_MODULE=citizensapi.settings            # which settings file should Django use
    DJANGO_WSGI_MODULE=citizensapi.wsgi                    # WSGI module name
    
    echo "Starting $NAME as `whoami`"
    
    # Activate the virtual environment
    cd $DJANGODIR
    source ../backendschoolvenv/bin/activate
    export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
    export PYTHONPATH=$DJANGODIR:$PYTHONPATH
    
    # Create the run directory if it doesn't exist
    RUNDIR=$(dirname $SOCKFILE)
    test -d $RUNDIR || mkdir -p $RUNDIR
    
    # Start your Django Unicorn
    # Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
    exec ../backendschoolvenv/bin/gunicorn --bind 0.0.0.0:8080 ${DJANGO_WSGI_MODULE}:application \
      --name $NAME \
      --workers $NUM_WORKERS \
      --user=$USER --group=$GROUP \
      --bind=unix:$SOCKFILE \
      --log-level=debug \
      --log-file=-
    ```
    
9. Установить supervisor и настроить автоматический запуск скрипта.
    
    ```
    # Устанавливаем supervisor
    sudo apt install supervisor
    # Создаем каталог и файл для логов
    mkdir ~/backendschooltest/logs/
    touch ~/backendschooltest/logs/gunicorn_supervisor.log
    # Создаем конфигурационный файл для запуска
    touch /etc/supervisor/conf.d/citizens_api.conf
    ```
   
    В citizens_api.conf добавить следующее:
    ```
    [program:citizens_api]
    command = ~/backendschooltest/backendschoolvenv/bin/gunicorn_start    ; Command to start app
    user = citizens_api                                                   ; User to run as
    stdout_logfile = ~/backendschooltest/logs/gunicorn_supervisor.log     ; Where to write log messages
    redirect_stderr = true                                                ; Save stderr in the same log
    environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8                       ; Set UTF-8 as default encoding
   ```

    Настроить запуск.
    
    ```
    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start citizensapi
    ```
    
10. После этого наш сервис стартует и будет доступен по адресу 0.0.0.0:8080. 
    Также будет автоматически запускаться при старте машины и восстанавливаться после сбоев.
    
___
####Список использованных ресурсов
1. http://michal.karzynski.pl/blog/2013/06/09/django-nginx-gunicorn-virtualenv-supervisor/

    