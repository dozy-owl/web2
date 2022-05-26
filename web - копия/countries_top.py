import sys
import sqlite3

from constants import D


def create_table():
    connection = sqlite3.connect('top_countries.sqlite')
    cur = connection.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS top_countries
                        (№ INT, Country TEXT,Ind INT, Population INT)''')
    table = cur.execute("""SELECT *
                            FROM top_countries""").fetchall()
    sep = ' '
    lst = []
    for line in table:
        lst.append(len(line[1]))
    max_len_country = max(lst)
    lst = []
    for line in table:
        lst.append(len(str(line[3])))
    max_len_population = max(lst)
    for i in range(len(table)):
        num = str(table[i][0])
        if len(num) == 1:
            add0 = 3
        elif len(num) == 2:
            add0 = 2
        else:
            add0 = 1
        new_num = sep + num + add0 * sep
        country = table[i][1]
        add1 = max_len_country + 2 - len(country)
        new_country = sep + country + add1 * sep
        ind = str(table[i][2])
        add2 = 7 - len(ind)
        new_ind = sep + ind + add2 * sep
        population = str(table[i][3])
        add3 = max_len_population + 2 - len(population)
        new_population = sep + population + add3 * sep
        table[i] = (new_num, new_country, new_ind, new_population)
    return table


def check_name(countries, list_countries, country):
    for i in countries:
            for j in i:
                list_countries.append(j)
    for i in list_countries:
        if i.lower() == country.lower():
            country = i
    for i in D.keys():
        if country.lower() == i:
            country = D[i]
    return country, list_countries


def show_country(country):
    connection = sqlite3.connect('top_countries.sqlite')
    cur = connection.cursor()
    countries = cur.execute("""SELECT Country
                                FROM top_countries""").fetchall()
    list_countries = []
    country, list_countries = check_name(countries, list_countries, country)
    if country not in list_countries:
            return 'Простите, но данных по этой стране нет.'
    answer = cur.execute("""SELECT  *
                         FROM top_countries WHERE Country = ?""",
                         (country,)).fetchone()
    s = ''
    for i in answer:
        s += str(i) + '      '
    return s
