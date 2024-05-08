from details import screen, screen_size
from details import font_20, font_15, font_10, font_25
from details import draw_text, Text_container, Button, Text_horizontal, draw_rect_with_border, rect_hover
import os
import shutil
import base
import colors
import pygame
import datetime
import calendar

months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]


def reset_selected(objects, event):
    active = []
    for i in objects:
        active.append(i.active)
        i.press(event)
    active2 = []
    for i in objects:
        active2.append(i.active)
    if active2.count(True) > 1:
        active2[active.index(True)] = False
        objects[active.index(True)].active = False
    return active2


def press_containers(objects, event):
    active = reset_selected(objects, event)
    if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB and True in active:
        objects[active.index(True)].active = False
        if active.index(True) + 1 >= len(active):
            objects[0].active = True
        else:
            objects[active.index(True) + 1].active = True


class Calendar:
    def __init__(self, coordinate, year, month, day):
        self.coordinate = coordinate
        self.date = datetime.date(int(year), months.index(month) + 1, int(day))
        self.day = day
        self.c = calendar.Calendar()
        self.hovered_idx = -1

    def set_date(self, year, month, day):
        month = month[0].upper() + month[1:].lower()
        if year == "":
            year = 1
        try:
            self.date = datetime.date(int(year), months.index(month) + 1, int(day))
        except:
            self.date = datetime.date(int(year), months.index(month) + 1, 1)
        self.day = self.date.day

    def draw(self, mouse_pos):
        d_n = 1
        y = self.coordinate[1]
        self.hovered_idx = -1
        for i in self.c.monthdatescalendar(self.date.year, self.date.month):
            x = self.coordinate[0]
            for l in i:
                x += 20
                if l.day == d_n:
                    color = colors.white if int(l.day) == int(self.day) else colors.white_green_2
                    rect = pygame.draw.rect(screen, color, (x, y, 20, 20))
                    if rect.collidepoint(mouse_pos[0], mouse_pos[1]):
                        self.hovered_idx = d_n
                        color = colors.white_green
                    draw_rect_with_border((x, y), 20, 20, color)
                    draw_text(str(l.day), [x + 10, y + 2], True, font_10)
                    d_n += 1
            y += 20

    def press(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered_idx >= 0:
                self.day = self.hovered_idx


class Tooltip_window:
    def __init__(self, coordinate=(), variants=(), width=300):
        self.open = False
        self.width = width
        self.coordinate = coordinate
        self.create_variants(variants)
        self.hovered = False
        self.hovered_idx = -1

    def hover(self, mouse_pos):
        self.hovered_idx = -1
        for i in range(len(self.correct_variants)):
            if rect_hover(mouse_pos, (self.coordinate[0], self.coordinate[1] + 30 * i), self.width, 30):
                self.hovered_idx = i
                break
            if i > 8:
                break
        return self.hovered_idx > -1

    def create_variants(self, variants):
        self.all_variants = []
        if len(variants) > 0:
            for i in sorted(variants):
                self.all_variants.append(Text_horizontal(i, font=font_20))
                self.all_variants[-1].crop_first()
        self.find_correct_variants()

    def find_correct_variants(self, text=""):
        self.correct_variants = []
        for i in self.all_variants:
            if text in i.text:
                self.correct_variants.append(i)

    def return_all_variants(self):
        variants = []
        for i in self.all_variants:
            variants.append(i.text)
        return variants

    def draw(self, line_number=0):
        for i in range(line_number, len(self.correct_variants) + line_number):
            color = colors.white_green if i == self.hovered_idx else colors.white
            draw_rect_with_border((self.coordinate[0], self.coordinate[1] + 30 * i), self.width, 30, color)
            draw_text(self.correct_variants[i].line, (self.coordinate[0] + 5, self.coordinate[1] + 30 * i),
                      font=font_20)
            if i > 8:
                break

    def press(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered_idx > -1:
                return self.correct_variants[self.hovered_idx].text


class Date_box:
    def __init__(self, coordinate, year=None, date=None):
        self.coordinate = coordinate
        self.year = str(year) if year else '2024'
        self.month = months[int(date.split('-')[1]) - 1] if date else months[0]
        self.day = date.split('-')[2] if date else 1
        if date:
            self.level = 2
        elif year:
            self.level = 1
        else:
            self.level = 0
        self.buttons = [
            Button("/" if year else "", self.coordinate, 30, font_20, 30),
            Button("/" if date else "", [self.coordinate[0], self.coordinate[1] + 50], 30, font_20, 30)
        ]
        self.day = Calendar((self.coordinate[0] + 510, self.coordinate[1] - 5), self.year, self.month, self.day)
        self.month = Text_container(self.month, [self.coordinate[0] + 230, self.coordinate[1] + 50], 200, 35, font_20)
        self.year = Text_container(self.year, (self.coordinate[0] + 230, self.coordinate[1]), 200, 35,
                                   font_20, mod="year")

    def return_active_box(self):
        return True in [self.month.active, self.year.active]

    def return_dates(self):
        if self.buttons[0].get_text == "" or self.buttons[1].get_text == "" or self.year.get_text == "":
            date = None
        else:
            date = datetime.date(int(self.year.get_text), months.index(self.month.get_text) + 1, self.day.day)
        return None if self.buttons[0].get_text == "" or self.year.get_text == "" else int(self.year.get_text), date

    def hover(self, mouse_pos):
        if self.level > 0:
            self.year.hover(mouse_pos)
            if self.level > 1:
                self.month.hover(mouse_pos)
        for i in range(len(self.buttons)):
            if i <= self.level:
                self.buttons[i].hover(mouse_pos)

    def draw(self, mouse_pos):
        birthday_texts = ["Знаю год", "Знаю дату"]
        x = self.coordinate[0] + 40
        y = self.coordinate[1]
        for i in range(self.level + 1 if self.level < 2 else self.level):
            self.buttons[i].draw()
            draw_text(birthday_texts[i], [x, y], False, font_20)
            y += 50
        if self.level > 0:
            self.year.draw()
            if self.level > 1:
                self.month.draw()
                if len(self.month.get_text) > 1 and self.year.get_text and int(self.year.get_text) > 0 and \
                        self.month.get_text[0].upper() + self.month.get_text[1:].lower() in months:
                    self.day.set_date(self.year.get_text, self.month.get_text, self.day.day)
                self.day.draw(mouse_pos)

    def press(self, event):
        self.day.press(event)
        press_containers([self.year, self.month], event)
        for i in self.buttons:
            if i.press(event):
                i.text.new_text("/" if not i.get_text else "")
            if self.buttons[0].get_text == "/":
                self.level = 1
                if self.buttons[1].get_text == "/":
                    self.level = 2
            else:
                self.level = 0


class New_last_name:
    def __init__(self, male="", female=""):
        self.male = Text_container(male, [540, 320], height=30, font=font_20, vertical=False)
        self.female = Text_container(female, [540, 370], height=30, font=font_20, vertical=False)
        self.accept = Button("Создать", [630, 420], 200, font_20, 30)
        self.back = Button("Отменить", [370, 420], 200, font_20, 30)

    def hover(self, mouse_pos):
        self.male.hover(mouse_pos)
        self.female.hover(mouse_pos)
        self.accept.hover(mouse_pos)
        self.back.hover(mouse_pos)

    def draw(self):
        draw_rect_with_border((350, 260), 500, 200)
        draw_rect_with_border((350, 260), 500, 48, colors.yellow)
        draw_text("Дабавление фамилии, дополните поля:", [600, 270], True, font_20)
        y = 320
        for i in ["Мужской вариант", "Женский вариант"]:
            draw_text(i, [530 - font_20.size(i)[0], y], font=font_20)
            y += 50
        for i in [self.male, self.female, self.accept, self.back]:
            i.draw()

    def press(self, db, event):
        if self.back.press(event):
            return False
        if self.accept.press(event) and self.male.get_text and self.female.get_text:
            base.append_last_names(db, self.male.get_text, self.female.get_text)
            result = base.find_last_name_by_text(db, self.male.get_text)
            return result if result else False
        press_containers([self.male, self.female], event)


class Create_window:
    def __init__(self, db, id: int = 0):
        self.db = db
        self.window = 0
        self.id = id
        self.buttons = [
            Button("X", [950, 110], 40, height=40),
            Button("Назад", [250, 560]),
            Button("Далее", [650, 560]),
            Button("М", [600, 330], 40, circle=True, colors=colors.gray),
            Button("Ж", [650, 330], 40, circle=True, colors=colors.gray)
        ]
        personality = base.find_person(db, self.id)
        if personality:
            name = base.find_name(db, personality[1])
            self.gender = bool(name[1])
            name = name[0]
            last_name = base.find_last_name(db, personality[2])
            last_name = last_name[0] if self.gender else last_name[1]
            self.biography = personality[8] if personality[8] else ""
            self.birthday = Date_box((220, 250), personality[3], personality[4])
            self.alive = bool(personality[5])
            self.death_day = Date_box((220, 450), personality[6], personality[7])
            phone = personality[9] if personality[9] else ""
            country_and_city = base.find_country_and_city_by_id(db, personality[10])
            image = personality[11] if personality[11] else ""
            self.window_name = "Изменение персоны"
        else:
            name = ""
            last_name = ""
            phone = ""
            image = ""
            country_and_city = ["", ""]
            self.biography = ""
            self.gender = True
            self.birthday = Date_box((220, 250))
            self.alive = True
            self.death_day = Date_box((220, 450))
            self.window_name = "Создание персоны"

        x = 600
        self.alive = Button("" if self.alive else "/", [220, 400], 30, font_20, 30)
        self.information = [
            Text_container(image, [x, 220], height=30, font=font_20, vertical=False),
            Text_container(phone, [x, 270], height=30, font=font_20, mod="phone", vertical=False),
            Text_container(country_and_city[0], [x, 220 + 50 + 50], height=30, font=font_20, vertical=False),
            Text_container(country_and_city[1], [x, 270 + 50 + 50], height=30, font=font_20, vertical=False)
        ]

        self.name = Text_container(name, [x, 220], height=35, font=font_20, colors=colors.standard, vertical=False)
        self.last_name = Text_container(last_name, [x, 270], height=35, font=font_20,
                                        colors=colors.standard, vertical=False)
        self.biography = Text_container(self.biography, [250, 400], 700, 130, font_20, colors.standard)

        self.name_templates = base.all_names(db, self.gender)
        if self.gender:
            self.buttons[-2].colors = colors.man
            self.last_name_templates = base.all_male_last_names(db)
        else:
            self.buttons[-1].colors = colors.woman
            self.last_name_templates = base.all_female_last_names(db)
        self.name_templates = Tooltip_window([x, 255], self.name_templates)
        self.last_name_templates = Tooltip_window([x, 305], self.last_name_templates)
        self.new_last_name = None

    def hover_chapter(self, chapter, chapter_templates, mouse_pos):
        if chapter.hover(mouse_pos) or chapter_templates.open:
            chapter_templates.open = True
            chapter_templates.find_correct_variants(chapter.get_text)
        if not chapter_templates.hover(mouse_pos):
            chapter_templates.hovered_idx = -1
            if not chapter.hover(mouse_pos):
                chapter_templates.open = False

    def hover(self, mouse_pos):
        if self.window == 0:
            self.hover_chapter(self.name, self.name_templates, mouse_pos)
            self.hover_chapter(self.last_name, self.last_name_templates, mouse_pos)
            self.biography.hover(mouse_pos)
            if self.window_name == "Создание персоны":
                for i in range(2):
                    self.buttons[(i + 1) * -1].hover(mouse_pos)
        elif self.window == 1:
            self.birthday.hover(mouse_pos)
            self.alive.hover(mouse_pos)
            if self.alive.get_text:
                self.death_day.hover(mouse_pos)
        elif self.window == 2:
            for i in self.information:
                i.hover(mouse_pos)
        elif self.window == 3:
            self.new_last_name.hover(mouse_pos)

        if self.window != 3:
            for i in [0, 2]:
                self.buttons[i].hover(mouse_pos)
            if self.window > 0:
                self.buttons[1].hover(mouse_pos)

    def draw_window_0(self):
        self.name.draw(self.name_templates.open or self.last_name_templates.open)
        self.last_name.draw(self.name_templates.open or self.last_name_templates.open)
        self.biography.draw(self.name_templates.open or self.last_name_templates.open)
        for i in range(2):
            self.buttons[(i + 1) * -1].draw(self.name_templates.open or self.last_name_templates.open)
        x = (screen_size[0] - 400) / 2 + 150
        y = 218
        for i in ["Имя:", "Фамилия:", "Пол:"]:
            draw_text(i, [x - font_25.size(i)[0], y], False)
            y += 50
        draw_text("Краткая биография:", [230, y], False, font_20)
        draw_text(f"{len(self.biography.text.text)}/255", [screen_size[0] - 300, 530], False, font_15)
        if self.name_templates.open:
            self.name_templates.draw()
        elif self.last_name_templates.open:
            self.last_name_templates.draw()

    def draw_window_1(self):
        mouse_pos = pygame.mouse.get_pos()
        self.birthday.draw(mouse_pos)
        self.alive.draw()
        draw_text("Человек умер?", [260, 400], font=font_20)
        draw_text("День рождения:", [220, 210], font=font_20)
        if self.alive.get_text:
            self.death_day.draw(mouse_pos)

    def draw_window_2(self):
        x = (screen_size[0] - 400) / 2 + 150
        y = 218
        for i in ["Адрес изображения персоны:", "Номер телефона:", "Страна рождения:", "Город рождения:"]:
            draw_text(i, [x - font_20.size(i)[0], y], False, font_20)
            y += 50
        for i in self.information:
            i.draw()

    def draw(self):
        draw_rect_with_border((200, 100), screen_size[0] - 400, screen_size[1] - 200)
        draw_rect_with_border((200, 100), screen_size[0] - 400, 100, colors.white_green)
        labels = ["Основная информация  ->", "Даты  ->", "Подробная информация"]
        color = colors.green_2
        x = (screen_size[0] - 400) / 3 + 20
        for i in range(len(labels)):
            if self.window == i:
                color = colors.black
            draw_text(labels[i], [x, 162], font=font_20, color=color)
            x += font_20.size(labels[i])[0] + 20

        self.buttons[2].draw()
        if self.window > 0:
            self.buttons[1].draw()

        windows = [self.draw_window_0, self.draw_window_1, self.draw_window_2]
        if self.window <= 2:
            windows[self.window]()
        elif self.window > 2:
            windows[2]()
            self.new_last_name.draw()

        draw_rect_with_border((200, 100), screen_size[0] - 400, 60, colors.white_green_2)
        draw_text(self.window_name, [200 + (screen_size[0] - 400) / 2, 110], True)
        self.buttons[0].draw()

    def press_chapter(self, chapter, chapter_templates, event):
        chapter.press(event)
        if chapter_templates.open:
            result = chapter_templates.press(event)
            if result is not None:
                chapter.text.new_text(result)
                return True

    def press(self, event):
        active2 = []
        if self.window == 0:
            active = [self.name.active, self.last_name.active, self.biography.active]
            if self.press_chapter(self.name, self.name_templates, event) or \
                    self.press_chapter(self.last_name, self.last_name_templates, event):
                return
            self.biography.press(event)
            active2 = [self.name.active, self.last_name.active, self.biography.active]
            if active2.count(True) > 1:
                blocks = [self.name, self.last_name, self.biography]
                blocks[active.index(True)].active = False
                active2[active.index(True)] = False
            if self.buttons[-2].press(event):
                self.gender = True
                self.buttons[-2].colors = colors.man
                self.buttons[-1].colors = colors.gray
                self.name_templates.create_variants(base.all_names(self.db, self.gender))
                self.last_name_templates.create_variants(base.all_male_last_names(self.db))
            elif self.buttons[-1].press(event):
                self.gender = False
                self.buttons[-1].colors = colors.woman
                self.buttons[-2].colors = colors.gray
                self.name_templates.create_variants(base.all_names(self.db, self.gender))
                self.last_name_templates.create_variants(base.all_female_last_names(self.db))
        elif self.window == 1:
            active = [self.birthday.return_active_box(), self.death_day.return_active_box()]
            self.birthday.press(event)
            self.death_day.press(event)
            active2 = [self.birthday.return_active_box(), self.death_day.return_active_box()]
            if active2.count(True) == 2:
                boxes = [self.birthday, self.death_day]
                boxes[active.index(True)].year.active = False
                boxes[active.index(True)].month.active = False
            if self.alive.press(event):
                self.alive.text.new_text("" if self.alive.get_text else "/")
        elif self.window == 2:
            active2 = press_containers(self.information, event)
        elif self.window == 3:
            result = self.new_last_name.press(self.db, event)
            if result == False:
                self.window = 2
                self.new_last_name = None
            elif result:
                l_n = base.find_last_name(self.db, result[0])
                self.last_name.text.new_text(l_n[0] if self.gender else l_n[1])
                self.create_person()
                return "close"
        if self.window != 3:
            if self.window > 0 and self.buttons[1].press(event):
                if self.buttons[2].text != "Далее":
                    self.buttons[2].text.new_text("Далее")
                self.window -= 1
            if self.buttons[2].press(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                self.window += 1
                if self.window > 1 and self.buttons[2].text.text != "Завершить":
                    self.buttons[2].text.new_text("Завершить")
                if self.window > 2 and (not self.last_name.get_text or not self.name.get_text):
                    self.window = 0
                    self.buttons[2].text.new_text("Далее")
                if self.window > 2:
                    if self.last_name.get_text in self.last_name_templates.return_all_variants():
                        self.create_person()
                        self.open = False
                        return "update"
                    self.new_last_name = New_last_name(self.last_name.get_text if self.gender else "",
                                                       self.last_name.get_text if not self.gender else "")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "close"
                elif event.key == pygame.K_TAB:
                    if self.window == 0 and True in active2:
                        blocks = [self.name, self.last_name, self.biography]
                        next = active2.index(True) + 1
                        if next >= len(blocks):
                            next = 0
                        blocks[active2.index(True)].active = False
                        blocks[next].active = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.buttons[0].hovered:
                return "close"

    def create_person(self):
        if (self.gender and self.name.get_text not in base.find_male_names(self.db)) or \
                (not self.gender and self.name.get_text not in base.find_female_names(self.db)):
            base.append_names(self.db, self.name.get_text, self.gender)
        name_id = base.find_name_by_text(self.db, self.name.get_text, self.gender)
        last_name_id = base.find_last_name_by_text(self.db, self.last_name.get_text)
        birthday = self.birthday.return_dates()
        death_date = self.death_day.return_dates()

        image = self.information[0].get_text
        if "/" not in image or image.split("/")[0] != "images":
            try:
                if "/" in image:
                    file = image.split("/")[-1]
                else:
                    file = image
                    image = f"images/{file}"
                if file not in os.listdir("images/"):
                    shutil.copy(image, f"images/{file}")
                image = file
            except:
                image = None
        else:
            image = image.split("/")[-1]
        if self.id == 0:
            base.append_person(self.db, name_id, last_name_id, birthday[0], birthday[1],
                               not self.alive.get_text, death_date[0], death_date[1],
                               self.biography.get_text, self.information[1:], image)
        else:
            base.update_person(self.db, self.id, name_id, last_name_id, birthday[0], birthday[1],
                               not self.alive.get_text, death_date[0], death_date[1],
                               self.biography.get_text, self.information[1:], image)
