import datetime
import pygame
import colors

import base
from details import screen, screen_size
from details import create_rect, draw_rect, draw_text, vertical_text, draw_rect_with_border, mouse_in_zone, rect_hover
from details import Text_container, Text_vertical, Text_horizontal, Button
from details import font_25, font_20, font_15, font_10

fonts = [font_25, font_20, font_15, font_10]


def split_box_text(text, width, height):
    split_text = Text_horizontal(text, width, fonts[0])
    for i in range(len(fonts)):
        split_text = Text_horizontal(text, width, fonts[i])
        if (fonts[i].get_height() <= height and split_text.line == text) or i >= len(fonts) - 1:
            break
    split_text.crop_first()
    if split_text.line != text:
        split_text.line = split_text.line[:-3] + "..."
    return split_text.line, split_text.font


def find_family_connection(db, person_1_id, id_person_looking_for, marriage=False, start_person_id=0, ids=[]):
    ids.append(person_1_id)
    per = Human(db, person_1_id)
    merr = base.find_marriages(db, person_1_id)
    for i in [per.children, per.other_children, per.parents, per.sibling, merr]:
        if id_person_looking_for in i:
            return False
    if id_person_looking_for not in merr and id_person_looking_for in per.spouses and \
            marriage and per.id == start_person_id:
        return True
    for i in [per.children, per.other_children, per.sibling, per.parents]:
        for l in i:
            if l not in ids:
                result = find_family_connection(db, l, id_person_looking_for)
                if not result:
                    return False
    return True


def check_the_connections(db, persons, connection_type, parental_connection=True, request_from_connections=False):
    if persons[0].mod != "block" and persons[1].mod != "block" and not request_from_connections:
        return "Связь персон уже существует"
    if not find_family_connection(db, persons[0].id, persons[1].id, connection_type == 2, persons[0].id) and \
            not request_from_connections:
        return "Связь персон уже существует"
    elif base.find_first(db) != 0 and persons[0].mod == "block" and persons[1].mod == "block":
        return "Персоны не прикреплены к структуре древа"

    if connection_type == 2:
        spouses = base.find_marriages(db, persons[0].id)
        if persons[1].id in spouses:
            return "Связь подобного типа уже существует"
        if persons[0].personality.gender == persons[1].personality.gender:
            return "Попытка создания связи персон одного пола"
        return True
    elif connection_type in [0, 1]:
        if connection_type + 1 > 1:
            connection_type = -1
        parents = base.find_parents(db, persons[connection_type + 1].id)
        if not parents:
            return True
        elif not parents[0] or not parents[1]:
            if parents[2] == parental_connection:
                per = Personality(db, parents[0] if parents[0] else parents[1])
                if per.gender == persons[connection_type].personality.gender:
                    return "Попытка создания родителей одного пола"
                return True
            else:
                return "Существует подобная связь, но не выбранного типа"
        else:
            return "При создании связи кол-во родителей будет превышено"
    return "Создание связи недопустимого типа"


class Wedding:
    def __init__(self, year=None, date=None, active=True):
        self.date = Date_knowledge(year, date)
        self.color = colors.white if active else colors.dark_gray
        self.hovered = False

    def hover(self, coordinate, size, mouse_pos):
        self.hovered = rect_hover(mouse_pos, (coordinate[0], coordinate[1] - 2), 50 + size, 10)

    def draw(self, coordinate, size):
        draw_rect_with_border((coordinate[0], coordinate[1] - 2), 50 + size, 10, self.color, 20)
        if self.hovered:
            x = coordinate[0] + 60
            font_size = font_15.size(self.date.return_date())[0]
            draw_rect_with_border((x - font_size / 2 - 5, coordinate[1] + 6), font_size + 10, 20)
            draw_text(self.date.return_date(), (x, coordinate[1] + 5), True, font_15)


class Draggable_block:
    def __init__(self, db, id):
        self.person_card = None
        self.id = id
        self.personality = Personality(db, id)
        self.color = colors.man if self.personality.gender else colors.woman
        self.name = split_box_text(self.personality.name, 200, 25)
        self.last_name = split_box_text(self.personality.last_name, 200, 25)
        self.hovered = [False, False]
        self.click = False
        self.delete_button = Button("X", (0, 0), 25, font_15, 25)

    @property
    def return_hover(self):
        return True in self.hovered

    def hover(self, mouse_pos, y):
        self.hovered = [False, False]
        if not self.click:
            x = screen_size[0] - 270
            self.hovered[0] = rect_hover(mouse_pos, (x, y), 205, 50)
            if self.hovered[0]:
                if self.person_card is None:
                    self.person_card = Person_card(self.personality)
                self.person_card.open = True
            elif self.person_card:
                self.person_card.open = False
            self.hovered[1] = rect_hover(mouse_pos, (x - 23, y + 10), 16, 30)
            self.delete_button.hover(mouse_pos)

    def draw_personal_card(self):
        if self.person_card and self.person_card.open:
            self.person_card.draw()

    def draw(self, y, mouse_pos, other_guidance=False):
        if not self.click:
            x = screen_size[0] - 293
        else:
            x = mouse_pos[0] - 8
            y = mouse_pos[1] - 15
        draw_rect([x + 23, y], [205, 50], self.color, self.hovered[0], False, False)
        draw_text(self.name[0], [x + 28, y], font=self.name[1])
        draw_text(self.last_name[0], [x + 28, y + 25], font=self.last_name[1])
        color = colors.white if self.hovered[1] and not other_guidance else colors.black
        draw_rect_with_border((x, y + 10), 16, 30, color, 6)
        self.delete_button.coordinate = (x + 205 + 25, y + 25 - 12.5)
        self.delete_button.draw()

    def press(self, event):
        if self.person_card and self.person_card.open:
            self.person_card.press(event)
        if self.delete_button.press(event):
            return "delete", self.id
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered[1]:
                self.click = True
            elif self.hovered[0]:
                self.person_card = None
                return "update", self.id
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.click:
            self.click = False
            if mouse_in_zone(False):
                return "push", self.id


class Personality:
    def __init__(self, db, id: int):
        human = base.find_person(db, id)
        self.name, self.gender = base.find_name(db, human[1])
        self.last_name = base.find_last_name(db, human[2])
        self.last_name = self.last_name[0] if self.gender else self.last_name[1]
        self.birthdate = Date_knowledge(human[3], self.str_to_date(human[4]))
        self.alive = human[5]
        self.death_date = Date_knowledge(human[6], self.str_to_date(human[7]))
        self.biography = human[8]
        self.information = []
        for i in range(9, 11):
            self.information.append(human[i])
        if self.information[1]:
            self.information[1] = base.find_country_and_city_by_id(db, self.information[1])
            self.information.append(self.information[1][0])
            self.information.append(self.information[1][1])
        else:
            self.information.append("")
            self.information.append("")
        self.information.pop(1)
        self.image = human[11]

    def str_to_date(self, text):
        if text:
            return datetime.datetime.strptime(text, "%Y-%m-%d").strftime('%d.%m.%Y')

    def __str__(self):
        return f"Personality( {self.name} {self.last_name}, {'М' if self.gender else 'Ж'} )"


class Human:
    def __init__(self, db, id: int, coordinate=(-180, -180), mod="normal", spouses_ids=(), parent_mod=["normal", 0]):
        # 4-е режима "normal", "children", "stop" и "block"
        self.id = id
        self.arrows_hovered = [False, False]
        self.size = [117, 43, 0]
        self.hovered = False
        self.box = None
        self.coordinate = coordinate
        self.wedding = None
        if not base.check_id(db, self.id):
            self.personality = None
        else:
            self.personality = Personality(db, id)
            self.color = colors.man if self.personality.gender else colors.woman
            self.name = split_box_text(self.personality.name, self.size[0], self.size[1] / 2)
            self.last_name = split_box_text(self.personality.last_name, self.size[0], self.size[1] / 2)
            self.mod = mod
            self.find_spouses(db)
            if mod == 'children':
                self.spouses.insert(0, 0)
            else:
                if len(spouses_ids) == 1:
                    self.spouses.insert(0, 0)
                elif len(spouses_ids) == 2:
                    for i in spouses_ids:
                        if i != self.id and i not in self.spouses:
                            self.spouses.insert(0, 0)
                        elif i in self.spouses:
                            self.spouses.insert(0, self.spouses.pop(self.spouses.index(i)))
            self.find_wedding(db)
            self.find_parents(db)
            self.find_children(db)
            self.find_sibling(db, parent_mod)

    def find_wedding(self, db):
        self.wedding = None
        if len(self.spouses) > 0 and self.mod == "normal":
            self.wedding = base.find_marriage_status(db, self.id, self.spouses[0])
        if self.wedding:
            self.wedding = Wedding(self.wedding[0], self.wedding[1], self.wedding[2])

    def update_human(self, db):
        self.personality = Personality(db, self.id)
        self.color = colors.man if self.personality.gender else colors.woman
        self.person_card = None
        self.name = split_box_text(self.personality.name, self.size[0], self.size[1] / 2)
        self.last_name = split_box_text(self.personality.last_name, self.size[0], self.size[1] / 2)

    def all_empty(self):
        for i in [self.spouses, self.parents, self.children, self.sibling]:
            if len(i) > 0:
                return False
        return True

    def arrow_hover(self, objects, hovered_idx, new_person_window_open=False):
        mouse_pos = pygame.mouse.get_pos()
        if not mouse_in_zone(not new_person_window_open):
            self.arrows_hovered[hovered_idx] = False
            return self.arrows_hovered[hovered_idx]
        for i in range(len(objects)):
            self.arrows_hovered[hovered_idx] = objects[i].collidepoint(mouse_pos[0], mouse_pos[1])
            if self.arrows_hovered[hovered_idx]:
                break
        return self.arrows_hovered[hovered_idx]

    def hover(self, mouse_pos):
        if type(self.box) == Mini_box and self.box.open:
            if self.box.hover(mouse_pos):
                self.hovered = False
                return False
        self.hovered = rect_hover(mouse_pos, (self.coordinate[0], self.coordinate[1]), self.size[0], self.size[1])
        if self.wedding:
            self.wedding.hover((self.coordinate[0] + self.size[0], self.coordinate[1] + self.size[1] + 10),
                               self.size[2], mouse_pos)
        return self.hovered

    # Функция поиска супругов человека
    def find_spouses(self, db):
        result = base.find_marriages(db, self.id)
        self.spouses = result
        result = base.find_children(db, self.id)
        for i in result.copy():
            result = base.find_parents(db, i)
            if result:
                for z in range(2):
                    if result[z] and result[z] != self.id and result[z] not in self.spouses:
                        self.spouses.append(result[z])
        self.find_wedding(db)

    # Функция поиска родителей человека
    def find_parents(self, db):
        self.parents = []
        result = base.find_parents(db, self.id)
        if result:
            for l in range(2):
                if result[l] and result[l] not in self.parents:
                    self.parents.append(result[l])
            self.parents_type_communication = result[2]

    # Функция поиска братьев/сестер человека
    def find_sibling(self, db, parent_mod=["normal", 0]):
        self.sibling = []
        result = []
        if len(self.parents) > 1 and parent_mod[0] != "children":
            result = base.find_sibling(db, self.parents[0], self.parents[1])
        elif len(self.parents) > 0:
            if parent_mod[0] == "children":
                result = base.find_children(db, self.parents[self.parents.index(parent_mod[1])])
            else:
                result = base.find_children(db, self.parents[0])
        for i in result:
            if i != self.id:
                self.sibling.append(i)

    # Функция поиска детей человека
    def find_children(self, db):
        self.children = []  # Все дети или дети от одного брака если человек был/состоит в браке
        self.other_children = []  # Дети не относящиеся к выбранному браку
        if self.mod == 'children' or len(self.spouses) == 0 or self.spouses[0] == 0:
            self.children = base.find_children(db, self.id)
        else:
            self.children = base.find_sibling(db, self.id, self.spouses[0])
            result = base.find_children(db, self.id)
            for i in result:
                if i not in self.children:
                    self.other_children.append(i)

    def apply_shift(self, shift=(0, 0)):
        self.coordinate = (self.coordinate[0] + shift[0], self.coordinate[1] + shift[1])

    def apply_size(self, size: int = 0):
        self.size = [self.size[0] - self.size[2] + size, self.size[1] - self.size[2] + size, size]
        self.name = split_box_text(self.personality.name, self.size[0], self.size[1] / 2)
        self.last_name = split_box_text(self.personality.last_name, self.size[0], self.size[1] / 2)

    def draw_box(self):
        if self.box and self.box.open:
            self.box.draw()

    def draw_arrow(self, x1, x2, turn, hovered=False):
        a = 2 + self.size[2] / 5
        y = self.coordinate[1] + self.size[1] / 2
        width = 15 + self.size[2] / 5
        size = (width, a * 2 if a > 0 else 2)
        rect = create_rect((x1, y - a), size)
        color = colors.green if hovered else colors.black
        rect = pygame.draw.rect(screen, color, rect)
        x2 = x2 + width if turn else x2 - width
        width = (3 + self.size[2] / 5) * 2
        if width < 2:
            width = 2
            y += 1
        b = 10 + self.size[2] / 5
        pol = pygame.draw.polygon(screen, color, ([x2, y + width], [x2, y - width], [x2 + b if turn else x2 - b, y]))
        return rect, pol

    def object_was_create(self, elements, family_ids):
        if len(elements) <= 0:
            return False
        for i in elements:
            if i in family_ids:
                return False
        return True

    def draw_array_with_step(self, array, family_ids, x, y, y_formul, width, width2):
        if self.object_was_create(array, family_ids):
            if width < 2:
                width = 2
                y += y_formul
            pygame.draw.polygon(screen, colors.black, ([x - width, y], [x + width, y], [x, y + width2]))

    def draw_lines(self, new_person_window_open=False, family_ids=()):
        if self.mod != "stop":
            if len(self.spouses) > 1:
                x = self.coordinate[0] + self.size[0] - 2
                if self.arrow_hover(self.draw_arrow(x, x - 2, True), 0, new_person_window_open):
                    self.draw_arrow(x, x - 2, True, self.arrows_hovered[0])
            if len(self.other_children) > 0:
                if self.arrow_hover(self.draw_arrow(self.coordinate[0] + 2 - (15 + self.size[2] / 5),
                                                    self.coordinate[0] + 4, False), 1, new_person_window_open):
                    self.draw_arrow(self.coordinate[0] + 2 - (15 + self.size[2] / 5),
                                    self.coordinate[0] + 4, False, self.arrows_hovered[1])
        else:
            if len(self.spouses) > 1:
                self.draw_arrow(self.coordinate[0] + self.size[0] - 2, self.coordinate[0] + self.size[0] - 2 - 2, True)
            if len(self.other_children) > 0:
                self.draw_arrow(self.coordinate[0] + 2 - (15 + self.size[2] / 5), self.coordinate[0] + 4, False)
            x = self.coordinate[0] + self.size[0] / 2
            width = (3 + self.size[2] / 5) * 2
            if width < 2:
                x += 2
            width_2 = 10 + self.size[2] / 5
            self.draw_array_with_step(self.spouses, family_ids, x, self.coordinate[1] + 54 + self.size[2],
                                      -1, width, width_2)
            ch = [i for i in self.children]
            for i in self.other_children:
                ch.append(i)
            self.draw_array_with_step(ch, family_ids, x, self.coordinate[1] + 54 + self.size[2],
                                      -1, width, width_2)
            self.draw_array_with_step(self.parents, family_ids, x, self.coordinate[1] + 2 - (15 + self.size[2] / 5),
                                      1, width, width_2 * -1)
        if len(self.children) > 0 or (len(self.spouses) > 0 and self.mod != "children"):
            width = 2 + self.size[2] / 5
            coord = self.coordinate[1] + self.size[1] - 2
            rect = create_rect(((self.coordinate[0] + self.size[0] / 2 - width), coord),
                               (width * 2 if width > 0 else 2, (15 + self.size[2] / 5)))
            pygame.draw.rect(screen, colors.black, rect)
            if self.mod != "stop" and len(self.children) > 0:
                height = 25 + self.size[2] - 2 * self.size[2] / 5
                x = self.coordinate[0] - width
                y = coord + (15 + self.size[2] / 5)
                size = (width * 2 if width > 0 else 2, height)
                if self.mod == "children" or len(self.spouses) == 0:
                    rect = create_rect((x + self.size[0] / 2, y), size)
                elif self.mod == "normal" and len(self.spouses) > 0:
                    rect = create_rect((x + self.size[0] + (50 + self.size[2]) / 2, y), size)
                pygame.draw.rect(screen, colors.black, rect)
        if len(self.parents) > 0:
            width = 2 + self.size[2] / 5
            height = 15 + self.size[2] / 5
            rect = create_rect(((self.coordinate[0] + self.size[0] / 2 - width), self.coordinate[1] + 2 - height),
                               (width * 2 if width > 0 else 2, height))
            pygame.draw.rect(screen, colors.black if self.parents_type_communication else colors.green, rect)

    def draw(self, other_guidance: bool = False, active: bool = False):
        if self.hovered and not other_guidance:
            if type(self.box) != Mini_box or not self.box or not self.box.open:
                if not self.box:
                    self.box = Person_card(self.personality)
                self.box.open = True
        elif not self.hovered and type(self.box) == Person_card and self.box and self.box.open:
            self.box.open = False
            self.box.window_1 = True
        draw_rect(self.coordinate, self.size, self.color, self.hovered, active, False, 3)
        x = self.coordinate[0] + self.size[0] / 2
        draw_text(self.name[0], [x, self.coordinate[1]], True, self.name[1])
        draw_text(self.last_name[0], [x, self.coordinate[1] + self.size[1] / 2], True, self.last_name[1])

    def press(self, event):
        if self.box and self.box.open:
            if type(self.box) == Mini_box:
                result = self.box.press(event)
                if result is not None:
                    return result
            else:
                self.box.press(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 3:
                self.box = Mini_box(self, pygame.mouse.get_pos())
            if event.button == 1:
                if self.arrows_hovered[0]:
                    return "right"
                elif self.arrows_hovered[1]:
                    return "left"

    @property
    def return_text(self):
        return f"{self.personality.name} {self.personality.last_name}, {'M' if self.personality.gender else 'Ж'}"

    def __str__(self):
        return f"Human( {self.personality}, {self.coordinate}, neighbours_ids = {self.parents}," + \
               f" {self.spouses}, {self.children}, {self.sibling}, mod={self.mod})"


class Family:
    def __init__(self, db):
        self.db = db
        self.active_id = base.find_first(db)
        self.mod = "review"
        self.click_line = []
        self.size = 0
        self.hovered_object_id = -1
        self.persons = []
        if base.check_id(db, self.active_id):
            self.persons.append(Human(self.db, self.active_id))
            self.append_persons(self.persons[0])
            self.centering()

    def hover(self, mouse_pos):
        self.hovered_object_id = -1
        for i in range(len(self.persons)):
            if self.persons[i].hover(mouse_pos):
                self.hovered_object_id = i
        return self.hovered_object_id

    def return_ids(self):
        ids = []
        for i in self.persons:
            ids.append(i.id)
        return ids

    def find_by_id(self, id):
        for i in self.persons:
            if i.id == id:
                return i

    def find_index_by_id(self, id):
        for i in range(len(self.persons)):
            if self.persons[i].id == id:
                return i

    def apply_shift(self, shift):
        if shift != [0, 0]:
            for i in self.persons:
                i.apply_shift(shift)

    def set_size(self, size):
        if -15 <= self.size + size <= 60:
            self.size += size
            if self.active_id > 0:
                self.apply_size(self.find_by_id(self.active_id))
            for i in self.persons:
                i.apply_size(self.size)

    def apply_size(self, person, shift_x=0, shift_y=0, idx=[], size=None):
        if size is None:
            size = self.size
        if person.id in idx:
            idx = []
        idx.append(person.id)
        if len(person.spouses) > 0 and person.spouses[0] != 0:
            if person.spouses[0] not in idx:
                per = self.find_by_id(person.spouses[0])
                if per:
                    per.apply_shift([(size - per.size[2]) * ((shift_x + 1) * 2),
                                     (size - per.size[2]) * (shift_y * 2)])
                    idx.append(person.spouses[0])

        n = 0
        for i in person.sibling:
            if i not in idx:
                per = self.find_by_id(i)
                if per:
                    per.apply_shift([(size - per.size[2]) * ((shift_x - 1 - n) * 2),
                                     (size - per.size[2]) * (shift_y * 2)])
                    idx.append(i)
                    n += 1

        n = 1
        if len(person.parents) == 1:
            per = self.find_by_id(person.parents[0])
            if per:
                n = 0 if len(per.children) == 1 else len(per.children) / 2 - 0.5
        elif len(person.parents) > 0 and len(person.sibling) + 1 >= 1:
            n = (len(person.sibling) + 1) / 2
        idx = self.apply_dimensions_to_people(n * -1, -1, person.parents, size, (shift_x, shift_y), idx)

        n = 1
        if len(person.children) == 1:
            per = self.find_by_id(person.children[0])
            n = 0 if per and len(per.parents) == 1 else 0.5
        elif len(person.children) > 1:
            n = len(person.children) / 2
            per = self.find_by_id(person.children[0])
            if per and (len(per.parents) == 1 or person.mod == "children"):
                n -= 0.5
        idx = self.apply_dimensions_to_people(n, 1, person.children, size, (shift_x, shift_y), idx)
        return idx

    def apply_dimensions_to_people(self, n, n_formul, peoples, size, shifts=(0, 0), idx=()):
        for i in peoples:
            if i not in idx:
                per = self.find_by_id(i)
                if per and per.mod != "stop":
                    per.apply_shift([(size - per.size[2]) * ((shifts[0] + n) * 2),
                                     (size - per.size[2]) * ((shifts[1] + n_formul) * 2)])
                    idx = self.apply_size(per, shifts[0] + n, shifts[1] + n_formul, idx, size)
                    n += n_formul
        return idx

    def centering(self):
        per = self.find_by_id(self.active_id)
        if per:
            shift = [per.coordinate[0] - (screen_size[0] // 2 - per.size[0] // 2),
                     per.coordinate[1] - (screen_size[1] // 2 - per.size[1] // 2)]
            for i in self.persons:
                i.coordinate = [i.coordinate[0] - shift[0], i.coordinate[1] - shift[1]]

    def step_by_x(self, person: Human, up=False):
        step = person.size[0] / 2 + 25
        if up:
            step *= -1
        person.coordinate = (person.coordinate[0] + step, person.coordinate[1])
        lines = [person.sibling, person.spouses]
        ids = self.return_ids()
        for i in lines:
            for l in i:
                if l in ids:
                    per = self.find_by_id(l)
                    per.coordinate = (per.coordinate[0] + step, per.coordinate[1])
        lines = person.parents if up else person.children
        for i in lines:
            if i in ids:
                per = self.find_by_id(i)
                if per.mod != "stop":
                    self.step_by_x(per, up)

    def update_spouses(self, person_1, person_2):
        if person_2.id not in person_1.spouses:
            person_1.spouses.append(person_2.id)
        if person_2.mod == "block":
            if person_2.id in self.return_ids() and person_2 not in self.persons:
                self.persons.pop(self.return_ids().index(person_2.id))
                self.append_persons(person_1)
            else:
                self.persons.pop(self.persons.index(person_2))

    def update_level(self, person_1, person_2, level):
        self.apply_size(self.persons[0], size=0)
        for i in self.persons:
            i.apply_size(0)

        # 0 - person_1 родитель; 1 - супруги
        if level == 0:
            if person_1.mod != "block":
                last_children = self.persons[self.find_index_by_id(person_1.id)].children.copy()
                if person_2.id not in last_children:
                    self.persons[self.find_index_by_id(person_1.id)].find_children(self.db)
                    self.persons.pop(self.find_index_by_id(person_2.id))
                    if person_1.mod != "stop":
                        if len(last_children) > 0:
                            sibling = self.persons[self.find_index_by_id(last_children[0])].sibling.copy()
                            person_2 = self.persons[self.find_index_by_id(last_children[0])]
                            self.persons[self.find_index_by_id(last_children[0])].find_sibling(self.db,
                                                                                               [person_1.mod,
                                                                                                person_1.id])
                            if len(sibling) != len(self.persons[self.find_index_by_id(last_children[0])].sibling):
                                self.step_by_x(person_2)
                                self.remove_persons(person_2, True, mine=False)
                                self.append_persons(self.persons[self.find_index_by_id(last_children[0])])
                        else:
                            self.append_persons(self.persons[self.find_index_by_id(person_1.id)])
                else:
                    self.persons[self.find_index_by_id(person_2.id)].find_parents(self.db)
            elif person_2.mod != "block":
                last_parents = self.persons[self.find_index_by_id(person_2.id)].parents.copy()
                self.persons[self.find_index_by_id(person_2.id)].find_parents(self.db)
                if person_1.id not in last_parents:
                    self.persons.pop(self.find_index_by_id(person_1.id))
                    if person_2.mod != "stop":
                        if len(last_parents) > 0:
                            self.persons[self.find_index_by_id(last_parents[0])].mod = "normal"
                            self.persons[self.find_index_by_id(last_parents[0])].find_spouses(self.db)
                            self.persons[self.find_index_by_id(last_parents[0])].find_children(self.db)
                            self.remove_persons(self.persons[self.find_index_by_id(person_2.id)], True)
                            person_1 = self.find_by_id(last_parents[0])
                            self.step_by_x(person_1, True)
                            self.append_persons(self.persons[self.find_index_by_id(last_parents[0])])
                            if self.find_by_id(person_2.id):
                                self.set_active(self.find_by_id(person_2.id))
                        else:
                            self.append_persons(self.persons[self.find_index_by_id(person_2.id)])
            elif person_1.mod == 'block' and person_2.mod == "block":
                self.active_id = person_1.id
                self.persons[self.find_index_by_id(person_1.id)].mod = "children"
                self.persons[self.find_index_by_id(person_1.id)].find_children(self.db)
                self.persons.pop(self.find_index_by_id(person_2.id))
                self.append_persons(self.persons[self.find_index_by_id(person_1.id)])
        elif level == 1:
            if len(person_1.spouses) > 0 or len(person_2.spouses) > 0:
                if len(person_1.spouses) > 0:
                    self.update_spouses(person_1, person_2)
                else:
                    self.update_spouses(person_2, person_1)
            else:
                person_1.find_spouses(self.db)
                person_2.find_spouses(self.db)
                active_person = self.find_by_id(self.active_id)
                if active_person:
                    self.apply_size(active_person, size=0)
                if person_1.mod != "block" or person_1.mod != "block":
                    if person_1.mod != "block":
                        self.active_id = person_1.id
                        self.persons.pop(self.find_index_by_id(person_2.id))
                    else:
                        self.active_id = person_2.id
                        self.persons.pop(self.find_index_by_id(person_1.id))
                    self.append_persons(self.find_by_id(self.active_id))
                else:
                    self.active_id = person_1.id
                    self.persons = [Human(self.db, person_1.id)]
                    self.append_persons(self.persons[0])
        for l in [0, self.size]:
            self.apply_size(self.persons[0], size=l)
            for i in self.persons:
                i.apply_size(l)

    def need_to_recreate(self, new_active_person: Human):
        ids = self.return_ids()
        per = Human(self.db, new_active_person.id)
        if len(per.parents) == 0 and new_active_person.mod == "stop":
            return False
        for i in per.parents:
            if i not in ids:
                return "parents"
        for i in per.children:
            if i not in ids:
                return "children"
        if new_active_person.mod == "stop":
            return "children"
        return True

    def create_correct_order_parents(self):
        ids = self.return_ids()
        for i in self.persons:
            if len(i.parents) > 0 and i.parents[0] in ids and self.find_by_id(i.parents[0]).mod == "stop":
                i.parents.append(i.parents.pop(0))
            for l in i.children.copy():
                if l in ids and self.find_by_id(l).mod == "stop":
                    i.children.append(i.children.pop(i.children.index(l)))

    def clear_last_persons(self, person: Human):
        ids = self.return_ids()
        for i in person.spouses:
            if i in ids:
                per = self.find_by_id(i)
                self.persons.pop(self.find_index_by_id(i))
                self.clear_last_persons(per)
        ids = self.return_ids()
        for i in person.children:
            if i in ids:
                per = self.find_by_id(i)
                self.persons.pop(self.find_index_by_id(i))
                self.clear_last_persons(per)

    def set_active(self, new_active_person: Human):
        active_person = self.find_by_id(self.active_id)
        if active_person:
            self.apply_size(active_person, size=0)
        for i in self.persons:
            i.apply_size(0)
        recreate = self.need_to_recreate(new_active_person)
        if len(new_active_person.spouses) > 0 and new_active_person.spouses[0] == 0:
            new_active_person.mod = "children"
        if new_active_person.mod == "stop":
            new_active_person.mod = "normal"
        self.active_id = new_active_person.id
        self.find_by_id(self.active_id).find_wedding(self.db)
        if recreate == "parents" or not recreate:
            if recreate == "parents":
                new_active_person = Human(self.db, self.active_id, [screen_size[0] // 2 - 58, screen_size[1] // 2 - 21])
            self.persons = [new_active_person]
            self.append_persons(self.persons[0])
        else:
            self.persons.insert(0, self.persons.pop(self.persons.index(new_active_person)))
            self.create_correct_order_parents()
            if recreate == "children" and len(self.persons) > 1:
                for i in self.persons[0].sibling:
                    per = self.find_by_id(i)
                    if per.mod != "stop":
                        self.persons[0].coordinate = self.find_by_id(i).coordinate
                        self.clear_last_persons(self.find_by_id(i))
                        self.remove_persons(self.persons[0], True, mine=False)
                        break
                self.append_persons(self.persons[0])
        for l in [0, self.size]:
            self.apply_size(new_active_person, size=l)
            for i in self.persons:
                i.apply_size(l)
        self.centering()

    def create_human(self, person_id, coordinate, mod="normal", spouses=(), parent_mod=["normal", 0]):
        self.persons.append(Human(self.db, person_id, coordinate, mod, spouses, parent_mod))

    def append_persons(self, person: Human):
        if person.personality is None:
            return None

        x = person.coordinate[0]
        if len(person.spouses) > 0 and person.spouses[0] != 0 and person.spouses[0] not in self.return_ids():
            self.create_human(person.spouses[0], [x + person.size[0] + 50, person.coordinate[1]], "stop")

        for i in person.sibling:
            if i not in self.return_ids():
                x -= person.size[0] + 50
                self.create_human(i, [x, person.coordinate[1]], "stop")

        if len(person.parents) > 0:
            shift = person.size[0] + 50 if len(person.parents) > 1 else 0
            if len(person.sibling) == 0:
                x = person.coordinate[0] - shift / 2
            else:
                formul = person.size[0] * (len(person.sibling) - 1) + 50 * len(person.sibling)
                x = person.coordinate[0] - formul / 2 - person.size[0] / 2
                x -= person.size[0] / 2 + 25 if len(person.parents) > 1 else shift

            parent = []
            for i in person.parents:
                parent.insert(0, i) if bool(base.find_gender_by_id(self.db, i)[0]) == True else parent.append(i)
            person.parents = parent

            par_children_reg = False
            for i in person.parents:
                if i in self.return_ids() and self.find_by_id(i).mod == "children":
                    par_children_reg = True
                    break

            if par_children_reg and len(person.parents) > 1:
                for i in person.parents.copy():
                    if i not in self.return_ids() or self.find_by_id(i).mod != "children":
                        person.parents.pop(person.parents.index(i))

            two_parent = False
            for i in person.parents:
                if i not in self.return_ids() and not par_children_reg:
                    regim = "normal" if len(person.parents) != 1 else "children"
                    self.create_human(i, [x, person.coordinate[1] - person.size[1] - 50],
                                      "stop" if two_parent else regim, person.parents)
                    self.append_persons(self.persons[-1])
                two_parent = True
                x += person.size[0] + 50

        if len(person.children) > 0:
            x = person.coordinate[0] + (person.size[0] * len(person.children) + 50 * (len(person.children) - 1)) / 2
            if len(person.spouses) == 0 or person.spouses[0] == 0:
                x -= person.size[0] // 2
            else:
                x += 50 // 2
            if person.children[0] not in self.return_ids():
                self.create_human(person.children[0], [x, person.coordinate[1] + person.size[1] + 50],
                                  parent_mod=[person.mod, person.id])
                self.append_persons(self.persons[-1])

    def remove_elements(self, elements, remove_my_line=False, top=False, bottom=False, mine=True):
        for i in elements:
            per = self.find_by_id(i)
            if per:
                self.remove_persons(per, remove_my_line, top, bottom, mine)

    def remove_persons(self, person: Human, remove_my_line=False, top=False, bottom=False, mine=True):
        if person.mod == "stop":
            return
        if top:
            self.remove_elements(person.parents, True, True)
        if bottom:
            self.remove_elements(person.children, True, bottom=True)
        if remove_my_line:
            if len(person.spouses) > 0 and person.spouses[0] != 0:
                per = self.find_index_by_id(person.spouses[0])
                if per:
                    self.persons.pop(per)
            for i in person.sibling:
                per = self.find_index_by_id(i)
                if per:
                    self.persons.pop(per)
            if mine:
                per = self.find_by_id(person.id)
                if per:
                    self.persons.pop(self.persons.index(per))

    def draw_persons_cards(self):
        min_box = False
        for i in self.persons:
            if type(i.box) == Mini_box and i.box.open:
                for l in self.persons:
                    l.hovered = False
                min_box = True
                break
        for i in self.persons:
            if min_box and type(i.box) == Person_card:
                i.box.open = False
            i.draw_box()

    def draw_line(self, x, y, formula):
        width = (2 + self.size // 5) * 2
        if width < 2:
            width = 2
            x += 2
        pygame.draw.rect(screen, colors.black, (x, y, formula, width))

    def draw(self, new_person_window_open=False):
        for i in range(len(self.persons)):
            x = self.persons[i].coordinate[0] + self.persons[i].size[0] // 2
            if len(self.persons[i].parents) > 0 and self.persons[i].mod != 'stop':
                formula = len(self.persons[i].sibling) * self.persons[i].size[0] + \
                          len(self.persons[i].sibling) * (50 + self.size)
                self.draw_line(x - formula, self.persons[i].coordinate[1] - 16 - self.size / 5 * 2, formula)
            if (len(self.persons[i].children) > 0 or len(self.persons[i].spouses) > 0) and self.persons[
                i].mod == 'normal':
                if len(self.persons[i].children) > 0:
                    per = self.find_by_id(self.persons[i].children[0])
                else:
                    per = self.find_by_id(self.persons[i].id)
                if per and (len(per.parents) > 1 or len(self.persons[i].spouses) > 0):
                    formula = 50 + self.size + self.persons[i].size[0]
                    self.draw_line(x, self.persons[i].size[1] + self.persons[i].coordinate[1] + 10, formula)

        ids = self.return_ids()
        for i in range(len(self.persons)):
            self.persons[i].draw_lines(new_person_window_open, ids)
            self.persons[i].draw(i != self.hovered_object_id, self.persons[i].id == self.active_id)

        for i in self.persons:
            if i.wedding:
                i.wedding.draw((i.coordinate[0] + i.size[0], i.coordinate[1] + i.size[1] + 10), i.size[2])

        if len(self.click_line) > 0:
            coord = self.click_line[0].coordinate
            pygame.draw.line(screen, colors.black, (coord[0] + 5, coord[1] + 5), pygame.mouse.get_pos(), 2)

    def press(self, event):
        for i in self.persons:
            result = i.press(event)
            if result is not None:
                self.hovered_object_id = -1
                if type(result) == int:
                    i.box = None
                    return result, i.id
                elif result in ["right", "left"]:
                    self.set_active(i)
                    self.apply_size(self.find_by_id(self.active_id), size=0)
                    for i in self.persons:
                        i.apply_size(0)
                    self.remove_persons(self.persons[0], True, bottom=True, mine=False)
                    if result == "right":
                        self.persons[0].mod = "normal"
                        if self.persons[0].spouses[0] == 0:
                            self.persons[0].spouses.pop(self.persons[0].spouses.index(0))
                        else:
                            self.persons[0].spouses.append(self.persons[0].spouses.pop(0))
                    elif result == "left":
                        zero = 0
                        if 0 in self.persons[0].spouses:
                            zero = self.persons[0].spouses.pop(self.persons[0].spouses.index(0))
                        self.persons[0].spouses.insert(0, zero)
                        self.persons[0].mod = "children"
                    self.persons[0].find_wedding(self.db)
                    self.persons[0].find_children(self.db)
                    self.append_persons(self.persons[0])
                    self.persons[0].arrows_hovered = [False, False]
                    for l in [0, self.size]:
                        self.apply_size(self.persons[0], size=l)
                        for i in self.persons:
                            i.apply_size(l)
                    break
                for i in self.persons:
                    i.box = None
            if type(i.box) == Mini_box and (not i.box.open or self.mod != "review"):
                i.box = None
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.mod == "review":
                    if self.hovered_object_id != -1 and self.persons[self.hovered_object_id].mod != "block":
                        self.set_active(self.persons[self.hovered_object_id])
                        return False
                elif self.hovered_object_id != -1:
                    self.click_line.append(self.persons[self.hovered_object_id])
                    if len(self.click_line) == 2:
                        if self.click_line[0] == self.click_line[1]:
                            self.click_line = []
                        else:
                            return self.click_line
            elif event.button == 3:
                self.click_line = []


class Date_knowledge:
    def __init__(self, year=0, date=None):
        self.year = year if year else None
        self.date = date

    def return_date(self, year_only: bool = False):
        if not self.year and not self.date:
            return "XXXX г." if year_only else "XX.XX.XXXX"
        if year_only or self.date is None:
            return f"{self.year} г."
        return str(self.date)

    def __str__(self):
        return f"Date( {self.date} )"


class Mini_box:
    def __init__(self, person: Human, coordinate):
        self.id = person.id
        self.open = True
        self.coordinate = [coordinate[0], coordinate[1]]
        if self.coordinate[0] + 150 > screen_size[0]:
            self.coordinate[0] -= 150
        self.hovered = False
        self.buttons = [Button("Изменить", self.coordinate, 150, font_15, 22)]
        if len(person.parents) + len(person.children) + len(person.spouses) > 0:
            self.buttons.append(Button("Настроить связи", self.coordinate, 150, font_15, 22))
            self.buttons.append(Button("Убрать все связи", self.coordinate, 150, font_15, 22))
            self.buttons.append(Button("Удалить", self.coordinate, 150, font_15, 22))
        y = coordinate[1]
        if y + 22 * len(self.buttons) > screen_size[1]:
            y = coordinate[1] - 22 * len(self.buttons)
        for i in self.buttons:
            i.coordinate = (i.coordinate[0], y)
            y += 21

    def hover(self, mouse_pos):
        self.hovered = False
        for i in self.buttons:
            i.hover(mouse_pos)
            if i.hovered:
                self.hovered = True
        return self.hovered

    def draw(self):
        for i in self.buttons:
            i.draw()

    def press(self, event):
        for i in range(len(self.buttons)):
            if self.buttons[i].press(event):
                return i
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
            self.open = False


class Person_card:
    def __init__(self, personality: Personality):
        self.fonts = [font_25, font_25]
        self.name, self.fonts[0] = split_box_text(personality.name, 200, 40)
        self.last_name, self.fonts[1] = split_box_text(personality.last_name, 200, 40)
        self.birthdate = personality.birthdate
        self.alive = personality.alive
        self.death_date = personality.death_date

        if not personality.biography or personality.biography == '':
            self.biography = f"Биография персоны: {self.name} {self.last_name}"
        else:
            self.biography = personality.biography
        self.biography = Text_container(self.biography, (0, 0), 282, 148, font_15, colors.standard)
        self.biography.line_number[0] = len(self.biography.text.lines) - self.biography.number_lines_in_container
        if self.biography.line_number[0] < 0:
            self.biography.line_number[0] = 0

        self.image = personality.image if personality.image and personality.image != '' else "none.png"
        try:
            self.image = pygame.image.load(f"images/{self.image}")
            self.image = pygame.transform.scale(self.image, (87, 87))
        except:
            self.image = None

        information = [
            f"Номер телефона:  {personality.information[0]}" if personality.information[0] else "",
            f"Страна рождения:  {personality.information[1]}" if personality.information[1] else "",
            f"Город рождения:  {personality.information[2]}" if personality.information[2] else ""
        ]
        while "" in information:
            information.pop(information.index(""))
        for i in range(len(information)):
            information[i] = Text_vertical(information[i], font=font_15).lines
        self.information = []
        for i in information:
            for l in i:
                self.information.append(l)
        self.line_number = len(self.information) - 168 // font_15.get_height()
        if self.line_number < 0:
            self.line_number = 0
        self.open = False
        self.window_1 = True

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        x = mouse_pos[0] + 10 if mouse_pos[0] + 320 <= screen_size[0] else mouse_pos[0] - 320
        y = mouse_pos[1] + 10 if mouse_pos[1] + 334 <= screen_size[1] else mouse_pos[1] - 334
        draw_rect_with_border((x, y), 310, 324, border_radius=5)
        pygame.draw.line(screen, colors.black, (x, y + 105), (x + 309, y + 105))
        x += 10
        y += 10
        try:
            screen.blit(self.image, (x, y))
        except:
            pygame.draw.rect(screen, colors.white, (x, y, 87, 87))
        pygame.draw.rect(screen, colors.black, create_rect([x, y], [87, 87]), 1)
        draw_text(self.name, [x + 97, y + 2], font=self.fonts[0])
        draw_text(self.last_name, [x + 97, y + 42], font=self.fonts[1])
        if len(self.information) > 0:
            pygame.draw.circle(screen, (153, 153, 153), (x + 135, y + 297), 5)
            pygame.draw.circle(screen, (153, 153, 153), (x + 155, y + 297), 5)
        self.draw_window_1(x, y) if self.window_1 else self.draw_window_2(x, y)

    def draw_window_1(self, x, y):
        self.biography.set_coordinate([x + 3, y + 131])
        dates = self.birthdate.return_date()
        if not self.alive:
            dates += f" - {self.death_date.return_date()}"
        draw_text(dates, [x + 145, y + 98], True, font_20)
        self.biography.draw()
        if len(self.information) > 0:
            pygame.draw.circle(screen, (160, 222, 160), (x + 135, y + 297), 5)

    def draw_window_2(self, x, y):
        vertical_text(self.information, [x, y + 108], 168 // font_15.get_height(), self.line_number, font=font_15)
        pygame.draw.circle(screen, (160, 222, 160), (x + 155, y + 297), 5)

    def press(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                if self.window_1:
                    self.biography.line_number[0] += 1
                    if len(self.biography.text.lines) < self.biography.line_number[0]:
                        self.biography.line_number[0] -= 1
                elif self.line_number < len(self.information) - 168 // font_15.get_height():
                    self.line_number += 1
            elif event.button == 5:
                if self.window_1:
                    if self.biography.line_number[0] > 0:
                        self.biography.line_number[0] -= 1
                elif self.line_number > 0:
                    self.line_number -= 1
        elif event.type == pygame.KEYDOWN and len(self.information) > 0:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a or \
                    event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.window_1 = not self.window_1
