import random
import threading
import time

import requests
from bs4 import BeautifulSoup

from professions_list.models import Profession, Skill

prof_result = []  # Список спаршенных вакансий


def get_soup(url, page_number=None):
    """
    Функция для получения соуп-объекта
    """
    headers = {
        # "cookie": "user_tags=%5B%7B%22id%22%3A0%2C%22add_date%22%3A%222021-02-21%22%2C%22name%22%3A%22careers_main_page_widget_control1%22%7D%2C%7B%22id%22%3A0%2C%22add_date%22%3A%222021-02-21%22%2C%22name%22%3A%22search_sortbutton_target2%22%7D%2C%7B%22id%22%3A0%2C%22add_date%22%3A%222021-02-21%22%2C%22name%22%3A%22careers_vacancies_widget_second_try_target%22%7D%2C%7B%22id%22%3A0%2C%22add_date%22%3A%222021-02-21%22%2C%22name%22%3A%22traffic_split%22%7D%5D; frontend:rabota-id:v1=6032ad9d668525006370958087130685; _ym_uid=161393398380142731; _ym_d=1613933983; tmr_lvid=da0dbb7917b9968dbd4caa0f5d2451cb; tmr_lvidTS=1613933982952; _ga=GA1.2.462693376.1613933983; _gid=GA1.2.1949039269.1613933983; _ym_isad=1; _fbp=fb.1.1613933983388.2070491282; frontend:region=www%3A3; device_view=full; _gcl_au=1.1.1078581313.1613934060; top100_id=t1.-1.928410586.1613934060555; last_visit=1613923260558::1613934060558; frontend:location:v4=null; tmr_detect=1%7C1613981038997; tmr_reqNum=15",

        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'
    }
    if page_number:
        url += page_number
    result = requests.get(url, headers=headers)
    result.encoding = 'utf8'
    text = result.text
    soup = BeautifulSoup(text, 'lxml')
    return soup


def threading_cycle(el):
    href = el.find('a')
    soup_el = get_soup("https://career.habr.com" + href["href"])
    block = soup_el.find('article', {'class': 'vacancy-show'})
    found = block.find_all('div', {'class': 'basic-section'})
    skill_block = ""
    company = ""
    skills = []
    for element in found:
        if element.find('span', {'class': 'inline-list'}):
            skill_block = element

            skills = [block.get_text() for block in
                      skill_block.find_all('a', {'class': 'link-comp link-comp--appearance-dark'})]
            company = skills[-1]
            skills = skills[:-1]

    description_block = soup_el.find("div", {'class': 'style-ugc'})
    block_string = ""
    for block in description_block:
        if block.name == "ul":
            for li in block:
                block_string += "-" + li.text + "\n"
        else:
            block_string += block.text + '\n'
    id_from_site = int(href["href"].split("/")[-1])
    description = block_string
    title = soup_el.find('h1', {'class': 'page-title__title'}).get_text()
    prof_result.append({"title": title, "company": company, "description": description, "skills": skills,
                        "id_from_site": id_from_site})
    # create_data(title, company, description, skills)


def create_data(title, company, description, skills, id_from_site):
    color_list = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]
    prof = Profession.objects.create(title=title, description=description, company=company, id_from_site=id_from_site)
    for skill in skills:
        skill_obj, created = Skill.objects.get_or_create(name=skill)

        if created:
            skill_obj.level = random.randint(1, 10)
            skill_obj.color = random.choice(color_list)
            skill_obj.save()

        prof.skills.add(skill_obj)
        prof.save()


def profession_getter(pages: int = 2):
    soup = get_soup("https://career.habr.com/vacancies?divisions[]=apps&page=")
    for page in range(1, pages):
        # print(page)
        soup = get_soup("https://career.habr.com/vacancies?divisions[]=apps&page=", str(page))
        professions_list = soup.find_all('div', {'class': 'vacancy-card__title'})
        threads = list()
        for el in professions_list:
            x = threading.Thread(target=threading_cycle, args=(el,))
            threads.append(x)
            x.start()
        for index, thread in enumerate(threads):
            thread.join(120)
            print(str(index) + " thread joining")
        for prof in prof_result:
            try:
                Profession.objects.get(id_from_site=prof["id_from_site"])
                continue
            except Profession.DoesNotExist:
                print("createing")
                create_data(**prof)
