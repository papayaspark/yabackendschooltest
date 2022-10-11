-- Создаем рабочую БД
create database if not exists citizens_api_db
character set utf8mb4;

-- TODO: надо ли создавать отдельную БД для тестов или достаточно дать пользователю права на ее создание?
-- Создаем тестовую БД
-- create database if not exists test_citizens_api_db
-- character set utf8mb4;

-- Создаем пользователся с соответствующими правами
create user if not exists `citizens_api`@`localhost` identified with mysql_native_password by 'n@z1$urf3r$%';
grant all on `citizens_api_db`.* to `citizens_api`@`localhost`;
grant all on `test_citizens_api_db`.* to `citizens_api`@`localhost`;
flush privileges;
