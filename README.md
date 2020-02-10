# okko

Проект по эмуляции событий интернет-магазина на базе данных Oracle, пересылка сгенерированных событий в kafka producer, с последующим чтением событий kafka consumer и отправка их в другую базу Oracle, а также в Hdfs.

Задачи
----------------------------------------------------------------------------------------------------------------------------
task_1: Реализация данных исходной (source) базы Oracle. 

1.Создание БД, создание пользователя, предоставление ему прав
2. Создание таблиц и определение типов данных

Структура таблиц исходной БД:

---Таблица событий (таблица фактов)---
CREATE TABLE FCT_EVENTS (
event_time DATE,
event_id NUMBER,
product_id NUMBER,
category_id NUMBER,
category_code VARCHAR2(25),
brand VARCHAR2(25),
price NUMBER,
customer_id NUMBER,
customer_session VARCHAR2(45)
);

---Справочник Покупатели---
CREATE TABLE DIM_CUSTOMERS (
customer_id NUMBER,
country VARCHAR2(20),
city VARCHAR2(20),
mail VARCHAR2(50),
phone VARCHAR2(25),
first_name VARCHAR2(20),
last_name VARCHAR2(20),
address VARCHAR2(50)
);

---Справочник Товары---
CREATE TABLE DIM_PRODUCTS (
product_id NUMBER,
category_id NUMBER,
category_code VARCHAR2(25),
brand VARCHAR2(25),
description VARCHAR2(250),
name VARCHAR2(100),
price NUMBER,
);

---Справочник поставщики---
CREATE TABLE DIM_SUPPLIERS (
suppliers_id NUMBER,
product_id NUMBER,
name VARCHAR2(100),
country VARCHAR2(20),
city VARCHAR2(20),
address VARCHAR2(50)
);

---Справочник событий---
CREATE TABLE EVENTS (
event_id NUMBER,
event_type VARCHAR2(15),
);

3. Наполнение исходных таблиц посредством PL/SQL пакета
4. Добавить job, для запуска пакета по расписанию, через dbms_job (генерация раз в 5-10 минут)

----------------------------------------------------------------------------------------------------------------------------
task_2: Написать producer kafka (producer_ok.py)

1. Создать на сервере kafka топик 'okko' 
2. Написать producer kafka на python (прописать коннект к source базе Oraclе, указать топик куда загружаем данные 'okko'). Продюсер должен производить инкрементную загрузку из таблиц Oracle в топик kafka. Справочники переносить через last update date, события магазина через id (они изменяться не могут)
3. Средствами Oozie Coordinator добавить задание на запуск producer_ok.py, с интервалом раз в три минуты.		

----------------------------------------------------------------------------------------------------------------------------
task_3: Написать consumer kafka (consumer_ko.py)

1. Создать на сервере в hdfs новый каталог 'okko' (hadoop fs -mkdir /user/usertest/okko)
2. Написать consumer kafka, который будет переносить таблицы в target базу Oracle и параллельно в hdfs. Оба покота в одном консьюмере. 
3. Средствами Oozie Coordinator добавить задание на запуск consumer_ko.py

----------------------------------------------------------------------------------------------------------------------------
task_4: Оптимизация и быстродействие исходной базы Oracle

1. Нужно попробовать создать таблицу с партицированием.
2. Рассмотреть вопрос, какие нужно поставить индексы (если это нужно).
3. Проверить скорость работы, через sql_trace и далее через tkprof.

----------------------------------------------------------------------------------------------------------------------------
task_5:  Рассчитываем аналитику в результирующей базе Oracle

В результирующей базе Oracle создать materialized view on commit с аналитикой по продажам
цифры по продажам за день, неделю, месяц и год.

----------------------------------------------------------------------------------------------------------------------------
task_6: Рассчитываем аналитику в hdfs

В hdfs рассчитываем аналитику по продажам: самые часто продаваемые товары по периодам.

----------------------------------------------------------------------------------------------------------------------------
task_7: В исходной и конечной базах Oracle, реализовать схему удаления "старых" данных

В source и target базах Oracle, можно продумать схему по удалению "старых" данных и хранить данные, скажем только за год. 
При увеличении потока данных такая проблема может всплыть (исчерпается диск в Oracle). Все данные по классике у нас должны остаться только в hdfs. 
Реализовать "очистку" можно, например, через pl/sql-пакет и dbms_job.
