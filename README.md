# Сравниваем вакансии программистов

Скрипт получет данные о вакансиях программистов по api с ресурсов [hh.ru](http://hh.ru/) и [superjob.ru](https://superjob.ru/) по г.Москва и расчитывает среднюю зараплату по каждой позиции.

### Как установить

Убедитесь что у вас установлен python версии 3.6.
Перейдите в папку с проектом.
Установите все необходимые зависимости:  
`pip3 install -r requirements.txt`  
Запустите скрипт `main.py` передав через пробел список интересующих вас языков программирования:  
`python3 main.py Java Python C++ Ruby JavaScript`  
Вывод:  
```
+HeadHunter Moscow------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| Java                  | 1706             | 323                 | 179918           |
| Python                | 1249             | 237                 | 155860           |
...
...

```
### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).

***

# Programming vacancies compare

The script is the recipient of data on the vacancies of programmers by API [hh.ru] (http://hh.ru/) and [superjob.ru] (https://superjob.ru/) in Moscow and calculates the average salary for each position .

### How to install

Make sure you have python version 3.6 installed.
Go to the project folder.
Install all the necessary dependencies:  
`pip3 install -r requirements.txt`  
Run the script `main.py` passing a list of programming languages of interest to you:  
`python3 main.py Java Python C++ Ruby JavaScript`    
Output example:  
```
+HeadHunter Moscow------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| Java                  | 1706             | 323                 | 179918           |
| Python                | 1249             | 237                 | 155860           |
...
...

```

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
