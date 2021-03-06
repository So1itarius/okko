# okko

Проект по эмуляции событий интернет-магазина на базе данных Oracle, пересылка сгенерированных событий в kafka producer, с последующим чтением событий kafka consumer и отправка их в другую базу Oracle, а также в Hdfs.

Задачи
----------------------------------------------------------------------------------------------------------------------------
task_1: Реализация данных исходной (source) базы Oracle. 

1.Создание БД, создание пользователя, предоставление ему прав
2. Создание таблиц и определение типов данных

Структура исходной БД:


**-- Последовательность для id таблицы Фактов --**

CREATE SEQUENCE fct_s_prod
    MINVALUE 1
    START WITH 1
    INCREMENT BY 1
    NOCACHE;
	
	
**-- Справочник Покупатели --**

CREATE TABLE DIM_CUSTOMERS ( 
	customer_id 		NUMBER, 
	country 			VARCHAR2(40), 
	city 				VARCHAR2(40), 
	phone 				VARCHAR2(40), 
	first_name 			VARCHAR2(40), 
	last_name 			VARCHAR2(40), 
	mail 				VARCHAR2(50), 
	last_update_date 	DATE,
	CONSTRAINT customer_pk PRIMARY KEY (customer_id)
);	


**-- Справочник Категорий --**

CREATE TABLE CATEGORY ( 
	category_id 	NUMBER, 
	category_code 	VARCHAR2(25), 
	CONSTRAINT category_pk PRIMARY KEY (category_id)
);


**-- Справочник Товары --**

CREATE TABLE DIM_PRODUCTS ( 
	product_id 			NUMBER, 
	category_id 		NUMBER, 
	brand 				VARCHAR2(30), 
	description 		VARCHAR2(100), 
	name 				VARCHAR2(50), 
	price 				NUMBER, 
	last_update_date 	DATE, 
	CONSTRAINT product_pk PRIMARY KEY (product_id)
);


**-- Последовательность для id таблицы Поставщики --**

CREATE SEQUENCE suppliers_s
	MINVALUE 1
	START WITH 1
	INCREMENT BY 1
	NOCACHE;
	
	
**-- Справочник Поставщики --**

CREATE TABLE DIM_SUPPLIERS ( 
	suppliers_id NUMBER, 
	category_id NUMBER, 
	name VARCHAR2(40), 
	country VARCHAR2(40), 
	city VARCHAR2(40), 
	last_update_date DATE,
	CONSTRAINT suppliers_pk PRIMARY KEY (suppliers_id)
);


**-- Справочник События --**

CREATE TABLE DIM_EVENT_TYPE (
    event_id     NUMBER,
    event_type   VARCHAR2(20), 
	CONSTRAINT event_id_pk PRIMARY KEY (event_id)
);  


**-- Таблица Фактов --**

CREATE TABLE FCT_PROD (
	id 			 NUMBER,
	event_id	 NUMBER,
    event_time   DATE, 
    product_id   NUMBER,
    customer_id  NUMBER,
	CONSTRAINT id_pk PRIMARY KEY (id)
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
