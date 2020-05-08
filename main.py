import requests
import os
import sys
from terminaltables import AsciiTable


#********** headhunter api functions **********

def get_response_hh(position, page=0):
    """
    Function for receiving requests from api HeadHunter (api.hh.ru).
    """
    base_url = 'https://api.hh.ru/vacancies/'
    params = {
        'area': 1,
        'period': 30,
        'text': position,
        'page': page,
    }
    response = requests.get(base_url, params=params, headers=None)
    response.raise_for_status()
    return response.json()


def predict_rub_salary_hh(vacancy):
    """
    The function considers the average salary for a vacancy received
    from api headhunter.
    """
    if vacancy['salary'] != None and vacancy['salary']['currency'] == 'RUR':
        if vacancy['salary']['from'] != None and vacancy['salary']['to'] != None:
            return (vacancy['salary']['from'] + vacancy['salary']['to']) / 2

        if vacancy['salary']['from'] != None and vacancy['salary']['to'] == None:
            return vacancy['salary']['from'] * 1.2

        if vacancy['salary']['from'] == None and vacancy['salary']['to'] != None:
            return vacancy['salary']['to'] * 0.8

    return None


def get_vacancies_hh(position):
    """
    Function receives all vacancies using pagination.
    """
    vacancies = []
    page = 0
    pages = 1
    while page < pages:
        response = get_response_hh(position, page)
        vacancies.extend(response['items'])
        page += 1
        pages = response['pages']

    return vacancies


#********** superjob api functions **********

def get_response_sj(position, auth_token, page=0):
    """
    Function for receiving requests from api SuperJob (api.superjob.ru).
    """
    base_url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': auth_token,
    }
    params = {
        'page': page,
        'town': 4,
        'catalogues': 48,
        'keyword': position,
    }
    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def predict_rub_salary_sj(vacancy):
    """
    The function considers the average salary for a vacancy received
    from api superjob.
    """
    if vacancy['payment'] == None:
        return None
    else:
        if vacancy['payment_from'] != 0 and vacancy['payment_to'] != 0:
            return vacancy['payment_from'] + vacancy['payment_to'] / 2

        if vacancy['payment_from'] != 0 and vacancy['payment_to'] == 0:
            return vacancy['payment_from'] * 1.2

        if vacancy['payment_from'] == 0 and vacancy['payment_to'] != 0:
            return vacancy['payment_to'] * 0.8


def get_vacansies_sj(position, auth_token):
    """
    Function receives all vacancies using pagination.
    """
    vacancies = []
    page = 0
    more = True
    while more:
        response = get_response_sj(position, auth_token, page)
        vacancies.extend(response['objects'])
        page += 1
        more = response['more']

    return vacancies


#********** common functions **********


def get_position_statistics(position, vacancies, func):
    """
    The function receives a list of all vacancies by line item
    and calculates statistics:
    found vacancies, processed vacancies, average salary.
    """
    vacancies_found = len(vacancies)
    vacancies_processed = 0
    total_salary = 0
    for vacancy in vacancies:
        projected_salary = func(vacancy)
        if projected_salary:
            vacancies_processed += 1
            total_salary += projected_salary

    if vacancies_processed == 0:
        average_salary = 0
    else:
        average_salary = int(total_salary / vacancies_processed)

    return {
        position.split()[1]: {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary,
        }
    }


def print_terminal_table(data, title):
    """
    Function prints statistics in the terminal.
    """
    table_data = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
    ]
    for key in data.keys():
        item = []
        item.append(key)
        item.append(data[key]['vacancies_found'])
        item.append(data[key]['vacancies_processed'])
        item.append(data[key]['average_salary'])
        table_data.append(item)

    print(AsciiTable(table_data, title).table)


#********** main **********


def main(positions, sj_auth_token):
    hh_data = {}
    sj_data = {}
    for position in positions:
        hh_vacancies = get_vacancies_hh(position)
        sj_vacancies = get_vacansies_sj(position, sj_auth_token)
        hh_position_statistics = get_position_statistics(position, hh_vacancies, predict_rub_salary_hh)
        sj_position_statistics = get_position_statistics(position, sj_vacancies, predict_rub_salary_sj)
        hh_data.update(hh_position_statistics)
        sj_data.update(sj_position_statistics)

    print_terminal_table(hh_data, 'HeadHunter Moscow')
    print_terminal_table(sj_data, 'SuperJob Moscow')


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    positions = ['Программист {}'.format(i) for i in sys.argv[1:]]
    try:
        main(positions, os.getenv('SJ_TOKEN'))
    except requests.exceptions.HTTPError as e:
        print(e)
