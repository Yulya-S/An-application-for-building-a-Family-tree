import pygame
import colors
from os import listdir, remove

import base
from details import font_25, font_20, font_15, font_10
from details import screen, screen_size, screen_size_2, draw_text, draw_rect_with_border, mouse_in_zone, rect_hover
from details import draw_arrows, Button, Text_container, Text_horizontal
from humans import Family, Draggable_block, Human, Personality, check_the_connections, Person_card
from create_window import Create_window, Date_box


# Счетчик связей которые будут затронуты
def count_connections_to_delete(db, start_id, del_id, start_del_id=0, ids=(), stop_after_del_id=False, start=True,
                                parent=True, children=True, spouse=True):
    if start_del_id == 0:
        start_del_id = del_id
        ids = [del_id]
    persons = []
    if parent:
        persons = base.find_parents(db, del_id)
        if persons:
            persons = [persons[0], persons[1]]
        else:
            persons = []
    if children:
        for person in base.find_children(db, del_id):
            persons.append(person)
    if spouse:
        for person in base.find_marriages(db, del_id):
            persons.append(person)
    if stop_after_del_id and not start and start_id in persons:
        return []

    for i in persons:
        if i and i not in ids and i != start_id:
            ids.append(i)
            result = count_connections_to_delete(db, start_id, i, start_del_id, ids, stop_after_del_id, False)
            if result != []:
                ids = result
            else:
                ids.pop(-1)
    return ids


# Выводит сообщения на экран
class Message:
    def __init__(self, index, text, data=None, box="", mod="are_you_sure"):
        self.index = index
        self.text = text
        self.data = data
        self.box = box
        self.mod = mod
        if mod == "are_you_sure":
            self.buttons = [
                Button("Нет", (screen_size_2[0] + 5, screen_size_2[1] - 2), 200, font_20),
                Button("Да", (screen_size_2[0] - 205, screen_size_2[1] - 2), 200, font_20)
            ]
            self.color = colors.yellow
        else:
            self.buttons = [Button("Ок", (screen_size_2[0] - 100, screen_size_2[1] - 2), 200, font_20)]
            self.color = colors.red

    def hover(self, mouse_pos):
        for i in self.buttons:
            i.hover(mouse_pos)

    def draw(self):
        size = 430 if font_20.size(self.text)[0] < 430 else font_20.size(self.text)[0] + 20
        draw_rect_with_border((screen_size_2[0] - size / 2, screen_size_2[1] - 60), size, 100)
        draw_rect_with_border((screen_size_2[0] - size / 2, screen_size_2[1] - 60), size, 50, self.color)
        draw_text(self.text, (screen_size_2[0], screen_size_2[1] - 53), True, font_20)
        for i in self.buttons:
            i.draw()

    def press(self, event):
        for i in range(len(self.buttons)):
            if self.buttons[i].press(event):
                return bool(i), self.data


# Выбор типа создаваемой связи
class Choosing_type_connection:
    def __init__(self, persons):
        self.persons = persons
        x = screen_size_2[0] - 250
        y = screen_size_2[1] - 77.5
        self.buttons = [Button(f"{self.persons[0].return_text} pодитель -> {self.persons[1].return_text}",
                               (x, y), 500, font_15)]
        self.buttons.append(Button(f"{self.persons[1].return_text} pодитель -> {self.persons[0].return_text}",
                                   (x, y + self.buttons[0].size[1] - 1), 500, font_15))
        y += self.buttons[0].size[1] + self.buttons[1].size[1] - 2
        for i in ["Супруги", "Назад"]:
            self.buttons.append(Button(i, (x, y), 500, font_15))
            y += font_15.get_height()

    def hover(self, mouse_pos):
        for i in self.buttons:
            i.hover(mouse_pos)

    def draw(self):
        draw_rect_with_border((screen_size_2[0] - 250, screen_size_2[1] - 126.5), 500, 50, colors.white_green)
        draw_text("Выберите тип создаваемой связи:", (screen_size_2[0], screen_size_2[1] - 117.5), True, font_20)
        for i in self.buttons:
            i.draw()

    def press(self, event):
        for i in range(len(self.buttons)):
            if self.buttons[i].press(event):
                return i


# Окно настроек родителя
class Create_parent_connection:
    def __init__(self, persons, mod, data=0, save_mod="connect", request_from_connections=False, connect_mod="normal"):
        self.request_from_connections = request_from_connections
        self.persons = persons
        self.mod = mod
        self.connect_mod = connect_mod
        x = screen_size_2[0] - 300
        y = screen_size_2[1] + 10
        self.buttons = [
            Button("Отмена", (x - 5, y), 200, font_15), Button("Приемные", (x + 405, y), 200, font_15),
            Button("Родные", (x + 200, y), 200, font_15)
        ]
        self.data = data
        self.save_mod = save_mod

    def hover(self, mouse_pos):
        for i in self.buttons:
            i.hover(mouse_pos)

    def draw(self):
        draw_rect_with_border((screen_size_2[0] - 310, screen_size_2[1] - 50), 620, 100)
        draw_rect_with_border((screen_size_2[0] - 310, screen_size_2[1] - 50), 620, 50, colors.white_green)
        draw_text("Выберите тип родительской связи:", (screen_size_2[0], screen_size_2[1] - 40), True, font_20)
        for i in self.buttons:
            i.draw()

    def press(self, event):
        for i in range(len(self.buttons)):
            if self.buttons[i].press(event):
                return i, self.data


# Окно настроек брака
class Create_spouse_connection:
    def __init__(self, db, persons, data=0, mod="connect"):
        self.persons = persons
        x = screen_size_2[0] + 2.5
        y = screen_size_2[1] - 100
        year = None
        date = None
        check_box = True
        d = None
        if mod != "connect":
            d = base.find_marriage_status(db, persons[0].id, persons[1].id)
        if d:
            year = d[0]
            date = d[1]
            check_box = bool(d[2])
        self.date = Date_box((x - 335, y), year, date)
        self.check_box = Button("" if check_box else "/", (x - 105, y + 105), 30, font_20)
        self.buttons = [
            Button("Отмена", (x - 205, y + 155), 200, font_20), Button("Сохранить", (x, y + 155), 200, font_20)
        ]
        self.data = data
        self.mod = mod

    def hover(self, mouse_pos):
        self.date.hover(mouse_pos)
        self.check_box.hover(mouse_pos)
        for i in self.buttons:
            i.hover(mouse_pos)

    def draw(self):
        draw_rect_with_border((screen_size_2[0] - 355, screen_size_2[1] - 170), 710, 280)
        draw_rect_with_border((screen_size_2[0] - 355, screen_size_2[1] - 170), 710, 50, colors.white_green)
        draw_text("Введите дату заключения брака:", (screen_size_2[0], screen_size_2[1] - 165), True)
        self.date.draw(pygame.mouse.get_pos())
        self.check_box.draw()
        draw_text("В разводе?", (screen_size_2[0] - 67.5, screen_size_2[1] + 7), font=font_20)
        for i in self.buttons:
            i.draw()

    def press(self, event):
        self.date.press(event)
        if self.check_box.press(event):
            self.check_box.text.new_text("" if self.check_box.get_text else "/")
        for i in range(len(self.buttons)):
            if self.buttons[i].press(event):
                return i, self.data


# Информация о связи сохраняющейся при решении конфликта
class Сommunication_information:
    def __init__(self, db, id):
        self.card = Person_card(Personality(db, id))
        name = Text_horizontal(self.card.name, 200, font=font_15)
        name.crop_first()
        last_name = Text_horizontal(self.card.last_name, 200, font=font_15)
        last_name.crop_first()
        self.text = f"{name.line} {last_name.line} {'M' if base.find_gender_by_id(db, id)[0] else 'Ж'}"

    def hover(self, mouse_pos, y):
        self.card.open = rect_hover(mouse_pos, (screen_size_2[0] - 141, y), 431, 30)

    def draw_person_card(self):
        if self.card.open:
            self.card.draw()

    def draw(self, y):
        draw_rect_with_border((screen_size_2[0] - 141, y), 431, 30)
        draw_text(self.text, (screen_size_2[0] - 136, y), font=font_15)


# Информация о конфликте
class Conflict:
    def __init__(self, db, ids):
        self.ids = ids
        self.persons = [Сommunication_information(db, i) for i in ids]
        if len(self.persons) == 1:
            self.persons = []
        self.hovered = False
        self.line_number = 0

    def hover(self, mouse_pos, y):
        self.hovered = rect_hover(mouse_pos, (screen_size_2[0] - 300, y), 150, 30)

        y = screen_size_2[1] - 162
        for i in range(self.line_number, len(self.persons)):
            self.persons[i].hover(mouse_pos, y)
            y += 29
            if i - self.line_number >= 9:
                break

    def draw_person_card(self):
        for i in self.persons:
            i.draw_person_card()

    def draw(self, y, am_i_selected=False):
        draw_rect_with_border((screen_size_2[0] - 300, y), 150, 30,
                              colors.white if not am_i_selected else colors.white_green_2)
        if self.hovered:
            pygame.draw.rect(screen, colors.green_2, (screen_size_2[0] - 300, y, 150, 30), 1)
        draw_text(str(len(self.ids) if len(self.ids) > 1 else 0), (screen_size_2[0] - 225, y), True, font_20)
        if am_i_selected:
            y = screen_size_2[1] - 162
            for i in range(self.line_number, len(self.persons)):
                self.persons[i].draw(y)
                y += 29
                if i - self.line_number >= 9:
                    break

        draw_arrows(self.line_number, len(self.persons) - self.line_number, 10, screen_size_2[0] + 291,
                    screen_size_2[1] - 154, screen_size_2[1] + 139)

    def press(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and \
                rect_hover(pygame.mouse.get_pos(), (screen_size_2[0] - 140, screen_size_2[1] - 161), 441, 310):
            if event.button == 5 and len(self.persons) - 10 - self.line_number > 0:
                self.line_number += 1
            elif event.button == 4 and self.line_number > 0:
                self.line_number -= 1
        return self.hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1


# Окно решения конфликта
class The_conflict_window:
    def __init__(self, db, id, mod="back"):
        self.db = db
        self.id = id
        self.mod = mod

        parent = base.find_parents(db, id)
        be_affected = []
        if parent:
            for i in range(2):
                if parent[i]:
                    be_affected.append(count_connections_to_delete(db, self.id, parent[i]))
        children = base.find_children(db, id)
        if len(children) > 1:
            ch = children.copy()
            for i in ch:
                par = base.find_parents(self.db, i)
                if par and par[0] and par[1]:
                    sb = base.find_sibling(self.db, par[0], par[1])
                    for l in sb:
                        if sb in children and ch.index(sb) > ch.index(l):
                            children.pop(children.index(sb))
        for l in [children, base.find_marriages(db, id)]:
            for i in l:
                be_affected.append(count_connections_to_delete(db, id, i))

        be_affected_copy = be_affected.copy()
        if len(be_affected) > 1:
            for i in range(len(be_affected)):
                for l in range(i + 1, len(be_affected)):
                    if len(be_affected[i]) > 0 and len(be_affected[l]) > 0 and be_affected[l][0] in be_affected[i] \
                            and be_affected[l] in be_affected_copy:
                        be_affected_copy.pop(be_affected_copy.index(be_affected[l]))
        for i in be_affected_copy.copy():
            if len(i) == 1:
                be_affected_copy.pop(be_affected_copy.index(i))

        self.conflicts = []
        for i in be_affected_copy:
            self.conflicts.append(Conflict(db, i))

        self.select = 0
        self.line_number = 0
        self.buttons = [
            Button("Отмена", (screen_size[0] / 2 - 290, screen_size[1] / 2 + 160), 200, font_20),
            Button("Подтвердить", (screen_size[0] / 2 + 90, screen_size[1] / 2 + 160), 200, font_20)
        ]

    def hover(self, mouse_pos):
        y = screen_size_2[1] - 162
        for i in range(self.line_number, len(self.conflicts)):
            self.conflicts[i].hover(mouse_pos, y)
            y += 29
            if i - self.line_number >= 9:
                break
        for i in self.buttons:
            i.hover(mouse_pos)

    def draw(self):
        x = screen_size_2[0] - 300
        y = screen_size_2[1] - 200
        draw_rect_with_border((x, y), 600, 350)
        draw_rect_with_border((x, y), 160, 350)
        draw_rect_with_border((x, y - 1), 160, 40, colors.white_green)
        draw_rect_with_border((x + 159, y - 1), 441, 40, colors.white_green)
        draw_rect_with_border((x, y + 349), 600, 55)
        y1 = screen_size_2[1] - 162
        for i in range(self.line_number, len(self.conflicts)):
            self.conflicts[i].draw(y1, self.select == i)
            y1 += 29
            if i - self.line_number >= 9:
                break
        draw_text("Связей сохранится:", (x + 75, y + 5), True, font_15)
        draw_text("Список связей которые будут сохранены:", (x + 379.5, y + 5), True, font_15)
        pygame.draw.polygon(screen, colors.black, ((x + 149, y + 210), (x + 149, y + 190), (x + 169, y + 200)))
        draw_arrows(self.line_number, len(self.conflicts) - self.line_number, 10, screen_size_2[0] - 149,
                    screen_size_2[1] - 154, screen_size_2[1] + 139)
        for i in self.buttons:
            i.draw()
        if len(self.conflicts) > 0:
            self.conflicts[self.select].draw_person_card()

    def press(self, event):
        if len(self.conflicts) < 2:
            return 2, [] if len(self.conflicts) < 1 else self.conflicts[0].ids
        for i in range(len(self.conflicts)):
            if self.conflicts[i].press(event):
                self.select = i
        for i in range(len(self.buttons)):
            if self.buttons[i].press(event):
                return i + 1, self.conflicts[self.select].ids
        if event.type == pygame.MOUSEBUTTONDOWN and \
                rect_hover(pygame.mouse.get_pos(), (screen_size_2[0] - 300, screen_size_2[1] - 161), 160, 310):
            if event.button == 5 and len(self.conflicts) - 10 - self.line_number > 0:
                self.line_number += 1
                self.select += 1
            elif event.button == 4 and self.line_number > 0:
                self.line_number -= 1
                self.select -= 1


# Связь и её отображения
class Connection:
    def __init__(self, db, id, variants, mod="normal"):
        self.coordinate = (screen_size_2[0] - 290, screen_size_2[1] - 151)
        self.db = db
        self.id = id
        self.mod = mod
        self.text = ""
        if self.id:
            self.new_personality(self.id)
        self.select = self.text == ""
        self.buttons = [
            Button("X", (screen_size_2[0] + 255, screen_size_2[1] - 148.5), 25, font_15, 25),
            Button("ОК", (screen_size_2[0] + 226, screen_size_2[1] - 148.5), 25, font_10, 25)
        ]
        self.line_number = 0
        self.personal_card = None
        self.variants = variants if self.select else None
        self.hovered = False

    def reset_coordinate(self, y):
        self.coordinate = (screen_size_2[0] - 290, screen_size_2[1] - 151 + y)
        for i in self.buttons:
            i.coordinate = (i.coordinate[0], screen_size_2[1] - 148.5 + y)

    def new_personality(self, id):
        self.id = id
        personality = Personality(self.db, id)
        self.text = f" {self.split_text(personality.name)} {self.split_text(personality.last_name)}" + \
                    f" {'М' if personality.gender else 'Ж'}"

    def split_text(self, text):
        t = Text_horizontal(text, 200, font=font_20)
        if t.text != t.line:
            t.crop_first()
            return t.line[:-3] + "..."
        return text

    def apply_shift(self, shift):
        self.coordinate = (self.coordinate[0], self.coordinate[1] + shift)
        for i in self.buttons:
            i.coordinate = (i.coordinate[0], i.coordinate[1] + shift)

    def hover(self, mouse_pos):
        self.hovered = rect_hover(mouse_pos, self.coordinate, 546 if not self.select else 517, 30)
        if self.hovered and self.text != "":
            self.personal_card = Person_card(Personality(self.db, self.id))
            self.personal_card.open = True
        if not self.hovered and self.personal_card:
            self.personal_card = None
        if self.select:
            self.buttons[1].hover(mouse_pos)
        self.buttons[0].hover(mouse_pos)

    def draw_personal_card(self):
        if self.personal_card and self.personal_card.open:
            self.personal_card.draw()

    def draw(self):
        if self.select:
            self.buttons[1].draw()
        self.buttons[0].draw()
        draw_rect_with_border(self.coordinate, 546 if not self.select else 517, 30)
        draw_text(self.text, (self.coordinate[0] + 10, self.coordinate[1]), font=font_20)

        if self.select:
            x = self.coordinate[0] + 10
            y = self.coordinate[1] + 15
            pygame.draw.polygon(screen, colors.black, ((x - 5, y), (x, y - 5), (x, y + 5)))
            x = self.coordinate[0] + 507
            pygame.draw.polygon(screen, colors.black, ((x + 5, y), (x, y - 5), (x, y + 5)))

    def press(self, event):
        if self.hovered and self.select:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    if self.id == 0 or len(self.variants) <= self.variants.index(self.id) + 1:
                        self.new_personality(self.variants[0])
                    else:
                        self.new_personality(self.variants[self.variants.index(self.id) + 1])
                elif event.key == pygame.K_LEFT:
                    if self.id == 0 or self.variants.index(self.id) - 1 < 0:
                        self.new_personality(self.variants[-1])
                    else:
                        self.new_personality(self.variants[self.variants.index(self.id) - 1])
        if self.hovered and not self.select and self.text and \
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return "update", self.id
        if self.buttons[1].press(event) and self.text:
            self.select = False
            return "connect", self.id
        if self.buttons[0].press(event):
            if self.text == "" or self.select:
                return "close"
            return "delete", self.id


# Окно со всеми связями
class All_connection:
    def __init__(self, db, id, start_window=0):
        self.db = db
        self.id = id
        self.line_number = 0
        self.window = start_window
        self.connections = [[], [], []]
        l = base.find_parents(db, id)
        if l is None:
            l = []
        else:
            l = [l[i] for i in range(2)]
        self.connections[0] = self.create_connections(db, l)
        self.connections[1] = self.create_connections(db, base.find_children(db, id))
        self.connections[2] = self.create_connections(db, base.find_marriages(db, id))

        x = screen_size_2[0] - 399
        x2 = screen_size_2[0] - 379

        for l in self.connections:
            y = 0
            for i in l:
                i.apply_shift(y)
                y += 35

        self.start_connections = self.connections
        self.buttons = [
            Button("Родители", (x2 if start_window == 0 else x, screen_size_2[1] - 145), 100, font_15),
            Button("Дети", (x2 if start_window == 1 else x, screen_size_2[1] - 114), 100, font_15),
            Button("Супруги", (x2 if start_window == 2 else x, screen_size_2[1] - 83), 100, font_15),
            Button("+!", (screen_size_2[0] + 210, screen_size_2[1] - 195), 40, font_25, 40,
                   hint="Создание сложной связи"),
            Button("+", (screen_size_2[0] + 210 - 45, screen_size_2[1] - 195), 40, font_25, 40),
            Button("X", (screen_size_2[0] + 255, screen_size_2[1] - 195), 40, font_25, 40)
        ]

    def create_connections(self, db, persons):
        while None in persons:
            persons.pop(persons.index(None))
        if persons:
            return [Connection(db, i, ()) for i in persons]
        return []

    def hover(self, mouse_pos):
        for i in range(self.line_number, len(self.connections[self.window])):
            self.connections[self.window][i].hover(mouse_pos)
            if i - self.line_number > 9:
                break
        for i in self.buttons:
            i.hover(mouse_pos)

    def draw(self):
        for i in self.buttons:
            i.draw()
        draw_rect_with_border((screen_size_2[0] - 300, screen_size_2[1] - 200), 600, 400)
        draw_rect_with_border((screen_size_2[0] - 290, screen_size_2[1] - 151), 570, 341)
        draw_rect_with_border((screen_size_2[0] - 300, screen_size_2[1] - 200), 600, 50, colors.white_green)
        self.buttons[-1].draw()
        self.buttons[-2].draw()
        self.buttons[-3].draw()
        for i in range(self.line_number, len(self.connections[self.window])):
            self.connections[self.window][i].draw()
            if i - self.line_number >= 9:
                break
        draw_arrows(self.line_number, len(self.connections[self.window]) - self.line_number, 10,
                    screen_size_2[0] + 288, screen_size_2[1] - 141, screen_size_2[1] + 189)
        for i in self.connections[self.window]:
            i.draw_personal_card()
        self.buttons[-3].draw_hint(pygame.mouse.get_pos())

    def find_ancestors(self, person_id, ids):
        person = Human(self.db, person_id)
        for l in ids.copy():
            for i in person.parents:
                if i:
                    if l[0] == i:
                        ids.pop(ids.index(l))
                        ids = self.find_ancestors(i, ids)
                    elif l[1] == i and l in ids:
                        z = ids[ids.index(l)]
                        ids[ids.index(l)] = (z[0], None, z[2])
                    elif l[2] == i and l in ids:
                        z = ids[ids.index(l)]
                        ids[ids.index(l)] = (z[0], z[1], None)
        for l in ids.copy():
            for i in person.children:
                if l[0] == i and l in ids:
                    ids.pop(ids.index(l))
                elif l[1] == i and l in ids:
                    z = ids[ids.index(l)]
                    ids[ids.index(l)] = (z[0], None, z[2])
                elif l[2] == i and l in ids:
                    z = ids[ids.index(l)]
                    ids[ids.index(l)] = (z[0], z[1], None)
        for l in ids.copy():
            for i in person.other_children:
                if l[0] == i and l in ids:
                    ids.pop(ids.index(l))
                elif l[1] == i and l in ids:
                    z = ids[ids.index(l)]
                    ids[ids.index(l)] = (z[0], None, z[2])
                elif l[2] == i and l in ids:
                    z = ids[ids.index(l)]
                    ids[ids.index(l)] = (z[0], z[1], None)
        return ids

    def find_descendants(self, person_id, ids):
        person = Human(self.db, person_id)
        for l in ids.copy():
            for i in person.children:
                if i and i in l:
                    if l in ids:
                        ids.pop(ids.index(l))
                    ids = self.find_descendants(i, ids)
            for i in person.other_children:
                if i and l[0] == i:
                    if l in ids:
                        ids.pop(ids.index(l))
                    ids = self.find_descendants(i, ids)
            for i in person.spouses:
                if i and i in l and l in ids:
                    ids.pop(ids.index(l))
        return ids

    def press(self, event):
        if self.buttons[-1].press(event):
            return "close" if self.start_connections == self.connections else self.id
        if self.buttons[-2].press(event):
            variants = base.find_person_without_communication(self.db)
            double_variants = []
            if self.window == 0:
                connection_ids = [i.id for i in self.connections[0]]
                for i in self.connections[0]:
                    for l in base.find_marriages(self.db, i.id):
                        if l not in connection_ids:
                            double_variants.append(l)
                    for l in base.find_children(self.db, i.id):
                        par = base.find_parents(self.db, l)
                        if par:
                            if par[0] and par[0] not in connection_ids and par[0] not in double_variants:
                                double_variants.append(par[0])
                            elif par[1] and par[1] not in connection_ids and par[1] not in double_variants:
                                double_variants.append(par[1])
            elif self.window == 2:
                for i in self.connections[1]:
                    result = base.find_parents(self.db, i.id)
                    if result:
                        double_variants.append(result[0] if result[0] != self.id else result[1])
            for i in variants:
                double_variants.insert(0, i)
            if double_variants:
                self.connections[self.window].append(Connection(self.db, 0, double_variants))
                self.connections[self.window][-1].apply_shift((len(self.connections[self.window]) - 1) * 35)
        if self.buttons[-3].press(event) and self.window == 0:
            variants = base.all_communications(self.db)
            variants = self.find_ancestors(self.id, self.find_descendants(self.id, variants))
            per = Human(self.db, self.id)
            for i in variants.copy():
                if self.id in i:
                    variants.pop(variants.index(i))
                elif i[0] in per.spouses or i[1] in per.spouses or i[2] in per.spouses:
                    variants.pop(variants.index(i))
                else:
                    for l in per.parents:
                        if l:
                            par = Human(self.db, l)
                            for z in par.children:
                                if i[0] == z and i in variants:
                                    variants.pop(variants.index(i))
                            for z in par.other_children:
                                if i[0] == z and i in variants:
                                    variants.pop(variants.index(i))
            double_variants = []
            for i in variants:
                for l in i:
                    if l and l not in double_variants:
                        double_variants.append(l)
            if double_variants:
                self.connections[self.window].append(Connection(self.db, 0, double_variants, "hard"))
                self.connections[self.window][-1].apply_shift((len(self.connections[self.window]) - 1) * 35)
        for i in range(len(self.buttons) - 3):
            if self.buttons[i].press(event):
                self.buttons[self.window].coordinate = (self.buttons[self.window].coordinate[0] - 20,
                                                        self.buttons[self.window].coordinate[1])
                self.window = i
                for z in self.connections:
                    y = 0
                    for l in z:
                        l.reset_coordinate(y)
                        y += 35
                self.line_number = 0
                self.buttons[i].coordinate = (self.buttons[i].coordinate[0] + 20, self.buttons[i].coordinate[1])
                break
        for i in self.connections[self.window]:
            result = i.press(event)
            if result:
                if type(result) != str:
                    return result[0], result[1], self.window, i.mod
                elif result == "close":
                    i = self.connections[self.window].index(i)
                    self.connections[self.window].pop(i)
                    if i < len(self.connections[self.window]):
                        for l in range(i, len(self.connections[self.window])):
                            self.connections[self.window][l].apply_shift(-35)
                    break
        if event.type == pygame.MOUSEBUTTONDOWN and \
                rect_hover(pygame.mouse.get_pos(), (screen_size_2[0] - 250, screen_size_2[1] - 200), 600, 350):
            if event.button == 5 and len(self.connections[self.window]) - 10 - self.line_number > 0:
                self.line_number += 1
                for i in self.connections[self.window]:
                    i.apply_shift(-35)
            elif event.button == 4 and self.line_number > 0:
                self.line_number -= 1
                for i in self.connections[self.window]:
                    i.apply_shift(35)


class New_person_window:
    def __init__(self, db):
        self.db = db
        self.update_person()
        self.buttons = [
            Button("+", [screen_size[0] - 35, 55], 30, height=40, hint="Создать новую персону"),
            Button("->", [screen_size[0] - 70, 55], 30, height=40, hint="Вернуть не прикрепленных")
        ]
        self.open = False
        self.line_number = 0

    def click(self):
        for i in self.persons:
            if i.click:
                return True
        return False

    def update_person(self):
        self.line_number = 0
        self.persons = base.find_person_without_communication(self.db)
        for i in range(len(self.persons)):
            self.persons[i] = Draggable_block(self.db, self.persons[i])

    def delete_by_id(self, id):
        ids = [i.id for i in self.persons]
        self.persons.pop(ids.index(id))

    def hover(self, mouse_pos):
        max_persons = 11 if len(self.persons) > 11 else len(self.persons)
        if not self.click():
            for i in self.buttons:
                i.hover(mouse_pos)
            y = 102
            for i in range(self.line_number, self.line_number + max_persons):
                self.persons[i].hover(mouse_pos, y)
                y += 52

    def draw(self, mouse_pos):
        max_persons = 11 if len(self.persons) > 11 else len(self.persons)
        draw_rect_with_border((screen_size[0] - 300, 50), 301, screen_size[1] - 99)
        draw_rect_with_border((screen_size[0] - 300, 50), 301, 50)
        for i in self.buttons:
            i.draw()

        y = 100
        for i in range(self.line_number, self.line_number + max_persons):
            if not self.persons[i].click:
                self.persons[i].draw(y, mouse_pos)
                y += 52
        if self.click():
            self.persons[-1].draw(y, mouse_pos)
        draw_arrows(self.line_number, len(self.persons) - self.line_number, 11, screen_size[0] - 10,
                    110, screen_size[1] - 60)
        for i in self.buttons:
            i.draw_hint(mouse_pos)
        for i in self.persons:
            i.draw_personal_card()

    def press(self, event):
        pos = pygame.mouse.get_pos()
        if not screen_size[1] - 50 > pos[1] > 50:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.click():
                self.persons[-1].click = False
                self.persons[-1].hovered = [False, False]

        for i in range(len(self.persons)):
            result = self.persons[i].press(event)
            if result:
                if result[0] == "push":
                    self.persons.pop(i)
                    if len(self.persons) - 11 - self.line_number != 0 and self.line_number != 0:
                        self.line_number -= 1
                elif result[0] == "delete":
                    if self.line_number != 0:
                        self.line_number -= 1
                    return result
                else:
                    self.persons[i].hovered = [False, False]
                return result

        for i in range(len(self.persons) - 1):
            if self.persons[i].click:
                self.persons.append(self.persons.pop(i))

        if self.buttons[0].press(event):
            return "update", 0
        if self.buttons[1].press(event):
            self.update_person()
            return "back"

        if event.type == pygame.MOUSEBUTTONDOWN and not self.click():
            if event.button == 5 and len(self.persons) - 11 - self.line_number > 0:
                self.line_number += 1
            elif event.button == 4 and self.line_number > 0:
                self.line_number -= 1


class Open_db:
    def __init__(self):
        self.cancel = Button("X", [screen_size_2[0] + 155, screen_size_2[1] - 245], width=40, height=40)
        self.line_number = 0
        self.create_objects()
        self.find_count()
        self.are_you_sure = None

    def create_objects(self):
        self.db_names = listdir("base")
        self.buttons = []
        self.del_buttons = []
        y = screen_size_2[1] - 201
        x = screen_size_2[0] - 200
        for i in self.db_names:
            self.buttons.append(Button(i, [x, y], 351, font_20))
            y2 = self.buttons[-1].size[1] / 2
            y2 += y - font_20.get_height() / 2
            self.del_buttons.append(Button("X", [x + 350, y2], 30, font_20, font_20.get_height()))
            y += self.buttons[-1].size[1] - 1

    def set_new_coordinate(self):
        y = screen_size_2[1] - 201
        for i in range(len(self.buttons)):
            self.del_buttons[i].hovered = False
            self.buttons[i].hovered = False
        for i in range(self.line_number, len(self.buttons)):
            self.buttons[i].coordinate[1] = y
            self.del_buttons[i].coordinate[1] = y + self.buttons[i].size[1] / 2 - font_20.get_height() / 2
            y += self.buttons[i].size[1] - 1

    def hover(self, mouse_pos):
        if not self.are_you_sure:
            for i in range(self.line_number, self.line_number + self.count):
                self.buttons[i].hover(mouse_pos)
                self.del_buttons[i].hover(mouse_pos)
            self.cancel.hover(mouse_pos)
        else:
            self.are_you_sure.hover(mouse_pos)

    def find_count(self):
        self.count = 0
        size = 0
        for i in range(self.line_number, len(self.buttons)):
            size += self.buttons[i].size[1]
            if size > 455:
                break
            self.count += 1

    def draw(self):
        x = screen_size_2[0] - 200
        y = screen_size_2[1] - 250
        draw_rect_with_border((x, y), 400, 500)
        draw_rect_with_border((x, y), 400, 50, colors.white_green)
        for i in range(self.line_number, self.line_number + self.count):
            self.buttons[i].draw()
            self.del_buttons[i].draw()
        draw_text("Открыть древо", [x + 180, y + 10], True, font_20)
        self.cancel.draw()
        draw_arrows(self.line_number, self.count + self.line_number, len(self.buttons), screen_size_2[0] + 187,
                    screen_size_2[1] - 190, screen_size_2[1] + 235)
        if self.are_you_sure:
            self.are_you_sure.draw()

    def press(self, event):
        if self.are_you_sure:
            result = self.are_you_sure.press(event)
            if result is not None:
                if result[0]:
                    try:
                        remove(f"base/{self.db_names[self.are_you_sure.index]}")
                        self.create_objects()
                        if self.line_number > 0:
                            self.line_number -= 1
                            self.set_new_coordinate()
                        self.find_count()
                    except:
                        self.are_you_sure = None
                self.are_you_sure = None
        if self.cancel.press(event):
            return False
        for i in range(len(self.buttons)):
            if self.buttons[i].press(event):
                return self.db_names[i]
            if self.del_buttons[i].press(event):
                self.are_you_sure = Message(i, "Вы уверены?")
                self.del_buttons[i].hovered = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4 and self.line_number > 0:
                self.line_number -= 1
                self.set_new_coordinate()
            if event.button == 5:
                count = 0
                size = 0
                for i in range(self.line_number, len(self.buttons)):
                    size += self.buttons[i].size[1]
                    if size > 450:
                        break
                    count += 1
                if count + self.line_number < len(self.buttons) and size >= 455:
                    self.line_number += 1
                    self.set_new_coordinate()
            self.find_count()


class Create_db:
    def __init__(self):
        self.error = ""
        x = screen_size_2[0] - 180
        y = screen_size_2[1] + 35
        self.buttons = [
            Button("Создать", [x + 210, y], 150, font_20, 28), Button("Отмена", [x, y], 150, font_20, 28)
        ]
        self.db_name = Text_container("", [x + 30, y - 55], height=35, font=font_20, vertical=False)

    def hover(self, mouse_pos):
        for i in self.buttons:
            i.hover(mouse_pos)
        self.db_name.hover(mouse_pos)

    def draw(self):
        x = screen_size_2[0] - 200
        y = screen_size_2[1] - 75
        draw_rect_with_border((x, y), 400, 150)
        draw_rect_with_border((x, y), 400, 40, colors.white_green)
        draw_text("Введите название нового древа:", (x + 200, y + 2), True, font_20)
        for i in self.buttons:
            i.draw()
        self.db_name.draw()
        draw_text(self.error, (x + 25, y + 83), font=font_15, color=(255, 0, 0))

    def press(self, event):
        if self.buttons[0].press(event):
            if self.db_name.get_text == "":
                self.error = "Название древа пусто!"
            elif self.db_name.get_text + ".db" in listdir("base"):
                self.error = "Древо с таким именем уже существует!"
            else:
                return self.db_name.get_text
        if self.buttons[1].press(event):
            return False
        self.db_name.press(event)


class Work_zone:
    def __init__(self, db_name=""):
        self.new_db(db_name)
        self.mini_window = None
        self.new_person_window = None
        self.mod = "review"
        self.shift = [0, 0]
        self.start_mouse_pos = 0
        self.buttons = [
            Button("Загрузить древо", (5, 12), 150, font_15), Button("Создать древо", (170, 12), 150, font_15),
            Button("Добавить данные из древа", (335, 12), 250, font_15, colors=colors.gray),
            Button("Обзор", (screen_size[0] - 370, 12), 70, font_15, hint="Смена режима"),
            Button("-", (screen_size[0] - 290, 12), 25, font_15, hint="Уменьшить древо"),
            Button("+", (screen_size[0] - 215, 12), 25, font_15, hint="Увеличить древо"),
            Button("[]", (screen_size[0] - 180, 12), 25, font_15, hint="Центрировать древо"),
            Button("?", (screen_size[0] - 145, 12), 25, font_15, hint="Справка", colors=colors.gray),
            Button("Персоны", (screen_size[0] - 110, 12), 100, font_15),
            Button("Аналитика", (screen_size[0] - 220, screen_size[1] - 37), 100, font_15, colors=colors.gray),
            Button("Опции", (screen_size[0] - 110, screen_size[1] - 37), 100, font_15, colors=colors.gray)
        ]

    def new_db(self, db_name):
        self.db = None
        self.family = None
        if db_name != "":
            self.db = base.Data_base(db_name)
            self.family = Family(self.db)
            self.family.set_active(self.family.persons[0])
        self.db_name = Text_horizontal(db_name, font=font_15)
        self.db_name.crop_first()
        if self.db_name.text != self.db_name.line:
            self.db_name.line += '...'

    def show(self, mouse_pos):
        screen.fill(colors.white)
        if self.mini_window:
            self.mini_window.hover(mouse_pos)
        if not self.mini_window:
            if self.new_person_window and self.new_person_window.open:
                self.new_person_window.hover(mouse_pos)
            for i in self.buttons:
                i.hover(mouse_pos)
            if self.family:
                if mouse_in_zone(not self.new_person_window or not self.new_person_window.open):
                    self.family.hover(mouse_pos)
                else:
                    for i in self.family.persons:
                        i.hovered = False
                        if i.box and i.box.open:
                            i.box = None
        if self.family:
            self.family.apply_shift(self.shift)
            self.shift = [0, 0]
            self.family.draw(self.new_person_window is not None)
        for i in [0, screen_size[1] - 50]:
            draw_rect_with_border((-1, i), screen_size[0] + 2, 51)
        for i in self.buttons:
            i.draw()
        if self.family:
            if self.mini_window and self.new_person_window:
                self.new_person_window.open = False
            if self.new_person_window and self.new_person_window.open:
                self.new_person_window.draw(mouse_pos)
            self.family.draw_persons_cards()
        text = f"{100 + self.family.size}%" if self.family else "100%"
        draw_text(text, (screen_size[0] - 240, 12), True, font_15)
        if self.db_name.text != "":
            draw_text(f"{self.db_name.line}.db", (10, screen_size[1] - 38), font=font_15)
        for i in self.buttons:
            i.draw_hint(pygame.mouse.get_pos())
        if self.mini_window:
            self.mini_window.draw()

    def back_objects(self):
        update = False
        for i in self.family.persons.copy():
            if i.all_empty():
                self.family.persons.pop(self.family.persons.index(i))
                update = True
        if update and self.new_person_window:
            self.new_person_window.update_person()
        self.family.click_line = []
        if self.new_person_window:
            self.new_person_window.update_person()

    def recreate_persons(self, person):
        self.family.persons = [Human(self.db, person)]
        self.family.append_persons(self.family.persons[0])
        self.family.set_active(self.family.persons[0])
        self.back_objects()

    def checking_mini_window(self, result):
        if type(self.mini_window) in [Create_db, Open_db]:
            if result != False:
                if type(self.mini_window) == Create_db:
                    self.new_db(result)
                else:
                    result = result.split(".")
                    if len(result) > 1 and result[1] == "db":
                        self.new_db(result[0])
            self.mini_window = None
            text = "Обзор" if not self.family or self.family.mod == "review" else "Связи"
            self.buttons[3].text.new_text(text)
        elif type(self.mini_window) == Message:
            if result[0]:
                if self.mini_window.box == "new person menu":
                    base.delete_person(self.db, self.mini_window.index)
                    if self.new_person_window:
                        self.new_person_window.delete_by_id(self.mini_window.index)
                elif self.mini_window.box == "communication menu":
                    per = None
                    next_per = True
                    if len(result[1][2]) > 0:
                        per = Human(self.db, result[1][2][0])
                        if result[1][1] == 0:
                            base.delete_parent_with_person_id(self.db, result[1][2][0], result[1][0])
                            if len(per.children) > 1:
                                next_per = False
                        elif result[1][1] == 1:
                            base.delete_parent_with_person_id(self.db, result[1][0], result[1][2][0])
                            if len(per.parents) > 1:
                                next_per = False
                        elif result[1][1] == 2:
                            base.delete_spouse_with_person_id(self.db, result[1][0], result[1][2][0])
                        result[1][2].pop(0)
                    if next_per:
                        for i in result[1][2]:
                            base.delete_parent(self.db, i)
                            base.delete_child(self.db, i)
                            base.delete_spouse(self.db, i)
                    if per.all_empty():
                        self.recreate_persons(result[1][0])
                    else:
                        self.recreate_persons(per.id)
                    self.back_objects()
                elif self.mini_window.box == "conflict menu":
                    all_person = base.all_person_id(self.db)
                    for i in result[1][0]:
                        if i in all_person:
                            all_person.pop(all_person.index(i))
                    for i in all_person:
                        base.delete_spouse(self.db, i)
                        base.delete_child(self.db, i)
                        base.delete_parent(self.db, i)
                    if result[1][1] == "delete":
                        base.delete_person(self.db, self.mini_window.index)
                    if len(result[1][0]) == 0:
                        if base.find_first(self.db):
                            self.recreate_persons(base.find_first(self.db))
                        else:
                            self.family.persons = []
                    else:
                        self.recreate_persons(result[1][0][0])
                    self.back_objects()
                    if len(self.family.persons) == 0 and base.find_first(self.db):
                        self.recreate_persons(base.find_first(self.db))
                self.mini_window = None
            elif self.mini_window.box == "communication menu":
                self.mini_window = All_connection(self.db, result[1][0], result[1][1])
            else:
                self.mini_window = None
        elif type(self.mini_window) == Create_window:
            if result == "update":
                ids = self.family.return_ids()
                if self.mini_window.id in ids:
                    self.family.persons[ids.index(self.mini_window.id)].update_human(self.db)
                self.back_objects()
                self.new_person_window = None
            self.back_objects()
            self.mini_window = None
        elif type(self.mini_window) == Choosing_type_connection:
            if result == 3:
                self.mini_window = None
            elif result in [0, 1]:
                self.mini_window = Create_parent_connection(self.mini_window.persons, result)
            elif result == 2:
                check = check_the_connections(self.db, self.mini_window.persons, result)
                if type(check) == bool:
                    self.mini_window = Create_spouse_connection(self.db, self.mini_window.persons)
                else:
                    self.mini_window = Message(0, check, mod="error")
        elif type(self.mini_window) == Create_parent_connection:
            if result[0] == 0:
                self.mini_window = None
            elif result[0] in [1, 2]:
                check = check_the_connections(self.db, self.mini_window.persons, self.mini_window.mod, result[0] - 1,
                                              self.mini_window.request_from_connections)
                if type(check) == bool or self.mini_window.save_mod == "update":
                    if self.mini_window.save_mod == "connect":
                        if self.mini_window.mod == 0:
                            persons = [self.mini_window.persons[1], self.mini_window.persons[0]]
                        else:
                            persons = [self.mini_window.persons[0], self.mini_window.persons[1]]
                        base.append_communications(self.db, persons[0].id, persons[1].id, result[0] - 1)
                        if self.mini_window.connect_mod != "hard":
                            self.family.update_level(persons[1], persons[0], 0)
                            per = self.family.find_by_id(persons[0].id)
                            if per:
                                per.find_sibling(self.db)
                                if per.mod != "stop":
                                    self.family.remove_persons(per, bottom=True, mine=False)
                                    self.family.append_persons(per)
                        else:
                            self.recreate_persons(persons[0].id)
                    else:
                        if self.mini_window.mod == 0:
                            persons = [self.mini_window.persons[1], self.mini_window.persons[0]]
                        else:
                            persons = [self.mini_window.persons[0], self.mini_window.persons[1]]
                        base.update_communications(self.db, persons[0].id, persons[1].id, result[0] - 1)
                        self.family.update_level(persons[1], persons[0], 0)
                    self.family.centering()
                    self.mini_window = None
                else:
                    self.mini_window = Message(0, check, mod="error")
            if result[1] != 0 and (type(self.mini_window) != Message or self.mini_window.mod != "error"):
                self.mini_window = All_connection(self.db, result[1])
        elif type(self.mini_window) == Create_spouse_connection:
            if result[0] == 1:
                if self.mini_window.mod == "connect":
                    func = base.append_marriages
                else:
                    func = base.update_marriages
                func(self.db, self.mini_window.persons[0].id, self.mini_window.persons[1].id,
                     self.mini_window.date.return_dates(), self.mini_window.check_box.get_text == "")
                self.family.update_level(self.mini_window.persons[0], self.mini_window.persons[1], 1)
                self.mini_window.persons[0].find_wedding(self.db)
                self.family.centering()
            if result[0] in [0, 1]:
                self.mini_window = None
            if result[1] != 0:
                self.mini_window = All_connection(self.db, result[1], 2)
        elif type(self.mini_window) == All_connection:
            if type(result) != tuple:
                self.mini_window = None
                if type(result) == int:
                    self.family.persons = [Human(self.db, result)]
                    self.family.append_persons(self.family.persons[0])
            else:
                if result[0] in ["connect", "update"]:
                    per = Human(self.db, result[1], mod="block")
                    if result[1] not in self.family.return_ids():
                        self.family.persons.append(per)
                    per2 = self.family.find_by_id(self.mini_window.id)
                    if result[2] == 2:
                        self.mini_window = Create_spouse_connection(self.db, [per2, per],
                                                                    self.mini_window.id, result[0])
                    else:
                        self.mini_window = Create_parent_connection([per, per2], result[2],
                                                                    self.mini_window.id, result[0], True, result[3])
                elif result[0] == "delete":
                    per = Human(self.db, self.mini_window.id)
                    par = len(per.parents) == 1 and self.mini_window.window == 0
                    child = len(per.children) == 1 and self.mini_window.window == 1
                    spo = len(per.spouses) == 1 and self.mini_window.window == 2
                    count = count_connections_to_delete(self.db, self.mini_window.id, result[1],
                                                        stop_after_del_id=True, parent=par, children=child, spouse=spo)

                    self.mini_window = Message(result[1], f"Кроме выбранной, персон будет затронуто:{len(count) - 1}",
                                               (self.mini_window.id, self.mini_window.window, count),
                                               "communication menu")
        elif type(self.mini_window) == The_conflict_window:
            if result[0] == 2:
                self.mini_window = Message(self.mini_window.id,
                                           f"Вы уверены? после подтвержения, отменить действие будет невозможно!",
                                           (result[1], self.mini_window.mod), "conflict menu")
            else:
                self.mini_window = None

    def press(self, event):
        if self.mini_window and self.family:
            self.family.click_line = []
        if not self.mini_window:
            if self.buttons[0].press(event):
                self.mini_window = Open_db()
                self.new_person_window = None
                return
            if self.buttons[1].press(event):
                self.mini_window = Create_db()
                self.new_person_window = None
                return
            if self.buttons[8].press(event):
                if self.db is not None and not self.new_person_window:
                    self.new_person_window = New_person_window(self.db)
                if self.new_person_window:
                    self.new_person_window.open = not self.new_person_window.open
                    if not self.new_person_window.open:
                        self.family.click_line = []
                    return

        if self.family and not self.mini_window:
            if self.buttons[3].press(event):
                self.family.mod = "review" if self.family.mod != "review" else "communication"
                self.buttons[3].text.new_text("Обзор" if self.family.mod == "review" else "Связи")
                self.family.click_line = []
                return
            if len(self.family.persons) > 0:
                if self.buttons[4].press(event):
                    self.back_objects()
                    self.family.set_size(-5)
                if self.buttons[5].press(event):
                    self.back_objects()
                    self.family.set_size(5)
                if self.buttons[6].press(event):
                    self.back_objects()
                    self.family.centering()
            result = self.family.press(event)
            if result:
                if type(result[0]) == int:
                    if result[0] == 0:
                        self.mini_window = Create_window(self.db, result[1])
                    elif result[0] == 1:
                        self.family.set_active(self.family.find_by_id(result[1]))
                        self.mini_window = All_connection(self.db, result[1])
                    elif result[0] == 2:
                        self.mini_window = The_conflict_window(self.db, result[1])
                    elif result[0] == 3:
                        self.mini_window = The_conflict_window(self.db, result[1], "delete")
                else:
                    self.family.click_line[1].hovered = False
                    self.family.click_line = []
                    self.mini_window = Choosing_type_connection(result)
            elif type(result) == bool and not result:
                self.back_objects()
            mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and \
                    mouse_in_zone(not self.new_person_window or not self.new_person_window.open):
                self.start_mouse_pos = mouse_pos
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.shift = [0, 0]
                self.start_mouse_pos = 0
            if self.start_mouse_pos != 0:
                self.shift = [mouse_pos[0] - self.start_mouse_pos[0], mouse_pos[1] - self.start_mouse_pos[1]]
                self.start_mouse_pos = mouse_pos
        if self.mini_window:
            result = self.mini_window.press(event)
            if result is not None:
                self.checking_mini_window(result)
        if self.new_person_window:
            result = self.new_person_window.press(event)
            if result:
                if result[0] == "push":
                    self.family.persons.append(Human(self.db, result[1], pygame.mouse.get_pos(), "block"))
                    self.family.persons[-1].apply_size(self.family.size)
                elif result[0] == "update":
                    self.mini_window = Create_window(self.db, result[1])
                elif result[0] == "delete":
                    self.mini_window = Message(result[1], "Вы уверены?", box="new person menu")
                elif result == "back":
                    self.back_objects()
