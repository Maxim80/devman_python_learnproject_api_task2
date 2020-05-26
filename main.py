import requests
import os
import sys
from terminaltables import AsciiTable


#********** headhunter api functions **********

def get_response_from_api_hh(position, page=0):
    """
    Parameters
    position: str
        job search position
    page: int
        page number

    Return
        dict: answer from HeadHunter API as dictionary
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


def get_vacancies_hh(position):
    """
    Parameters
    position: str
        job searc

    Return
        list: all vacancies list
    """
    vacancies = []
    page = 0
    pages = 1
    while page < pages:
        response = get_response_from_api_hh(position, page)
        vacancies.extend(response['items'])
        page += 1
        pages = response['pages']

    return vacancies


def get_expected_salaries_hh(vacancies):
    """
    Parameters
    vacancies: list
        all vacancies list

    Return
        list: list of expected vacancies
        [
            {'from': 100000, 'to': 180000, 'currency': 'RUR', 'gross': False},
            {'from': 60000, 'to': 120000, 'currency': 'RUR', 'gross': False},
            ...
            ...
        ]
    """
    expected_salaries = []
    for vacancy in vacancies:
        if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
            expected_salary = {
                'from': vacancy['salary']['from'],
                'to': vacancy['salary']['to'],
                'currency': vacancy['salary']['currency'],
                'gross': vacancy['salary']['gross'],
            }
            expected_salaries.append(expected_salary)

    return expected_salaries


#********** superjob api functions **********

def get_response_from_api_sj(position, auth_token, page=0):
    """
    Parameters
    position: str
        job search position
    auth_token: str
        authentication token
    page: int
        page number

    Return
        dict: answer from SuperJob API as dictionary
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


def get_vacancies_sj(position, auth_token):
    """
    Parameters
    position: str
        job searc
    auth_token: str
        authentication token

    Return
        list: all vacancies list
    """
    vacancies = []
    page = 0
    more = True
    while more:
        response = get_response_from_api_sj(position, auth_token, page)
        vacancies.extend(response['objects'])
        page += 1
        more = response['more']

    return vacancies


def get_expected_salaries_sj(vacancies):
    """
    Parameters
    vacancies: list
        all vacancies list

    Return
        list: list of expected vacancies
        [
            {'from': 100000, 'to': 180000, 'currency': 'RUR', 'gross': False},
            {'from': 60000, 'to': 120000, 'currency': 'RUR', 'gross': False},
            ...
            ...
        ]
    """
    expected_salaries = []
    for vacancy in vacancies:
        if vacancy['currency'] == 'rub':
            expected_salary = {
                'from': vacancy['payment_from'],
                'to': vacancy['payment_to'],
                'currency': vacancy['currency'],
                'gross': None,
            }
            expected_salaries.append(expected_salary)

    return expected_salaries


#********** common functions **********


def predict_rub_salary(expected_salary):
    """
    Parameters
    expected_salary: dict
        dictionary with expected salary

    Return
        float: predicted salary
    """
    if expected_salary['from'] != None and expected_salary['to'] != None:
        return (expected_salary['from'] + expected_salary['to']) / 2

    if expected_salary['from'] != None and expected_salary['to'] == None:
        return expected_salary['from'] * 1.2

    if expected_salary['from'] == None and expected_salary['to'] != None:
        return expected_salary['to'] * 0.8


def get_average_salary(expected_salaries):
    """
    Parameters
    expected_salaries: list
        list of expected salaries

    Return
        average_salary: int, average salary for all vacancies
        vacancies_processed: int, number of vacancies processed
    """
    total_salary = 0
    for expected_salary in expected_salaries:
        total_salary += predict_rub_salary(expected_salary)

    vacancies_processed = len(expected_salaries)
    average_salary = int(total_salary / vacancies_processed)

    return average_salary, vacancies_processed


def get_general_statistics(position, vacancies_found, expected_salaries):
    """
    Parameters
    position: str
        position for displaying statistics
    vacancies_found: int
        number of vacancies found
    expected_salaries: list
        list of expected salaries

    Return
        dict: general statistics
        {'Python': {
            'average_salary': 154208,
            'vacancies_found': 1243,
            'vacancies_processed': 235
            }
        }
    """
    average_salary, vacancies_processed = get_average_salary(expected_salaries)
    programming_lang = position.split()[1]
    return {
        programming_lang: {
            'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': average_salary,
        }
    }


def print_terminal_table(statistics, title):
    """
    Parameters
    statistics: dict
        dictionary with general statistics for all vacancie
    title: str
        title table

    Return
        None
    """
    table_for_print = [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
    ]
    for programm_lang, programm_lang_stat in statistics.items():
        stat_row = []
        stat_row.append(programm_lang)
        stat_row.append(programm_lang_stat['vacancies_found'])
        stat_row.append(programm_lang_stat['vacancies_processed'])
        stat_row.append(programm_lang_stat['average_salary'])
        table_for_print.append(stat_row)

    print(AsciiTable(table_for_print, title).table)


#********** main **********


def main():
    from dotenv import load_dotenv
    load_dotenv()

    positions = ['Программист {}'.format(i) for i in sys.argv[1:]]
    hh_all_statistics = {}
    sj_all_statistics = {}
    for position in positions:
        hh_vacancies = get_vacancies_hh(position)
        sj_vacancies = get_vacancies_sj(position, os.getenv('SJ_TOKEN'))
        hh_expected_salary = get_expected_salaries_hh(hh_vacancies)
        sj_expected_salary = get_expected_salaries_sj(sj_vacancies)
        hh_statistics = get_general_statistics(position, len(hh_vacancies), hh_expected_salary)
        sj_statistics = get_general_statistics(position, len(sj_vacancies), sj_expected_salary)
        hh_all_statistics.update(hh_statistics)
        sj_all_statistics.update(sj_statistics)

    print_terminal_table(hh_all_statistics, 'HeadHunter Moscow')
    print_terminal_table(sj_all_statistics, 'SuperJob Moscow')


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.HTTPError as e:
        print(e)
