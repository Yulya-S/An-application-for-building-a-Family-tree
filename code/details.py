import pygame
import pyperclip
import datetime
from colors import black, standard, white

pygame.init()
screen_size = [1200, 720]
screen_size_2 = [screen_size[0] / 2, screen_size[1] / 2]

screen = pygame.display.set_mode(screen_size, pygame.SCALED)

font_5 = pygame.font.SysFont('Comic Sans MS', 5)
font_10 = pygame.font.SysFont('Comic Sans MS', 10)
font_15 = pygame.font.SysFont('Comic Sans MS', 15)
font_20 = pygame.font.SysFont('Comic Sans MS', 20)
font_25 = pygame.font.SysFont('Comic Sans MS', 25)
font_30 = pygame.font.SysFont('Comic Sans MS', 30)


def draw_arrows(first_line, last_line, line_count, x, y1, y2):
    if first_line > 0:
        pygame.draw.polygon(screen, black, [(x, y1), (x + 6, y1), (x + 3, y1 - 5)])
    if last_line > line_count:
        pygame.draw.polygon(screen, black, [(x, y2), (x + 6, y2), (x + 3, y2 + 5)])


def mouse_in_zone(new_person_window_open: bool):
    mouse_pos = pygame.mouse.get_pos()
    return screen_size[1] - 50 >= mouse_pos[1] >= 50 and (new_person_window_open or mouse_pos[0] < screen_size[0] - 300)


def draw_rect_with_border(coordinate: tuple, width: int, height=50, color=white, border_radius=0):
    pygame.draw.rect(screen, color, (coordinate[0], coordinate[1], width, height), 0, border_radius)
    pygame.draw.rect(screen, black, (coordinate[0], coordinate[1], width, height), 1, border_radius)


def rect_hover(mouse_pos, coordinate: tuple, width: int, height=50):
    rect = pygame.Rect(coordinate[0], coordinate[1], width, height)
    return rect.collidepoint(mouse_pos[0], mouse_pos[1])


# Распределение координат и Размеров в создании прямоугольника
def create_rect(coordinate, size):
    return (coordinate[0], coordinate[1], size[0], size[1])


def draw_rect(coordinate, size, colors, hover: bool, active: bool, border: bool = True, border_width: int = 1):
    pygame.draw.rect(screen, colors[0], create_rect(coordinate, size))
    if active:
        pygame.draw.rect(screen, colors[-1], create_rect(coordinate, size), border_width)
    elif hover:
        pygame.draw.rect(screen, colors[-2], create_rect(coordinate, size), border_width)
    elif border:
        pygame.draw.rect(screen, colors[1], create_rect(coordinate, size), border_width)


def draw_circle(coordinate, ragius, colors, hover: bool, border: bool = True):
    coord = [coordinate[0] + ragius / 2, coordinate[1] + ragius / 2]
    circle = pygame.draw.circle(screen, colors[0], coord, ragius)
    if hover:
        pygame.draw.circle(screen, colors[-1], coord, ragius, 2)
    elif border:
        pygame.draw.circle(screen, colors[-2], coord, ragius, 2)
    return circle


def draw_text(text, coordinate, center: bool = False, font=font_25, color=black):
    text_b = font.render(text, True, color)
    text_rect = text_b.get_rect(center=(coordinate[0], coordinate[1] + font.get_height() // 2))
    if not center:
        text_rect.left = coordinate[0]
    screen.blit(text_b, text_rect)


def vertical_text(lines, coordinate, number_lines_in_container, line_number,
                  color=black, font=font_25, center: bool = False, shift: int = 300):
    lines = list(reversed(lines))
    if line_number + number_lines_in_container > len(lines):
        line_number = len(lines) - number_lines_in_container

    x = coordinate[0] + shift - 15
    y = coordinate[1] + 8
    y1 = coordinate[1] + font.get_height() * (number_lines_in_container - 1) + 10
    if number_lines_in_container == 1:
        y1 += font.get_height()
    draw_arrows(line_number, len(lines) - number_lines_in_container, line_number, x, y, y1)
    for i in range(number_lines_in_container):
        y = coordinate[1] + font.get_height() * (number_lines_in_container - i - 1)
        if line_number + i >= 0:
            draw_text(lines[line_number + i], (coordinate[0], y), center, font, color)


# Класс с самостоятельно подготавливающимся текстом для текстовых блоков
class Text_vertical:
    def __init__(self, text: str, width: int = 300, font=font_25, mod: str = 'text'):
        self.width = width
        self.mod = mod
        self.font = font
        self.new_text(text)

    def new_text(self, text: str, ):
        self.text = text
        self.lines = self.split_to_size(text)
        if self.mod == "password":
            for i in range(len(self.lines)):
                for l in range(len(self.lines[i])):
                    self.lines[i][l] = '*'

    def new_size(self, width):
        self.width = width
        self.lines = self.split_to_size(" ".join(self.text))

    def find_line(self, char_number=0):
        summ = 0
        number = 0
        for i in list(reversed(self.lines)):
            if summ <= char_number <= summ + len(i):
                return [number, char_number - summ]
            number += 1
            summ += len(i)
        return [0, 0]

    def find_char_number(self, line_number=0):
        lines = list(reversed(self.lines))
        summ = 0
        for i in range(0, line_number):
            summ += len(lines[i])
        return summ

    def split_to_size(self, text, sep: str = ' '):
        words = text.split(sep) if sep != "" else text
        lines = []
        new_line = []
        for i in words:
            new_line.append(i)
            if self.font.size(sep.join(new_line))[0] > self.width - 10:
                lines.append(sep.join(new_line[:-1]) + sep)
                new_line = new_line[-1:]

                if self.font.size(new_line[0])[0] > self.width - 10:
                    new_line = self.split_to_size(new_line[0], '')
                    for l in range(len(new_line) - 1):
                        lines.append(new_line[l])
                    new_line = new_line[-1:]

        lines.append(sep.join(new_line))
        while '' + sep in lines:
            lines.pop(lines.index('' + sep))
        return lines


class Text_horizontal:
    def __init__(self, text: str, width: int = 300, font=font_25, mod: str = 'text'):
        self.width = width
        self.mod = mod
        self.font = font
        self.new_text(text)

    def new_text(self, text: str, char_number=0):
        self.text = text
        self.find_max_line_number()
        self.split_to_size(char_number)
        if self.mod == "password":
            for i in range(len(self.line)):
                self.line[i] = "*"

    def new_size(self, width, char_number=0):
        self.width = width
        self.find_max_line_number()
        self.split_to_size(char_number)

    def find_max_line_number(self):
        if self.font.size(self.text)[0] < self.width:
            self.max_line_number = len(self.text) + 1
            return
        self.max_line_number = 0
        start_text = ""
        for i in self.text:
            start_text += i
            if self.font.size(start_text)[0] <= self.width + 10:
                self.max_line_number += 1
            else:
                self.max_line_number -= 1
                break

    def crop_first(self):
        new_text = ""
        for i in self.text:
            if self.font.size(new_text + i)[0] >= self.width - 10:
                break
            new_text += i
        self.line = new_text

    def split_to_size(self, char_number=0):
        rev_text = ""
        for i in range(len(self.text), 0, -1):
            rev_text += self.text[i - 1]

        l_n = char_number
        if l_n + self.max_line_number > len(self.text) + 1:
            l_n = len(self.text) - self.max_line_number + 1

        new_text = ""
        for i in range(len(rev_text)):
            if i + l_n > len(rev_text) - 1:
                break
            new_text += rev_text[i + l_n]
            if self.font.size(new_text)[0] >= self.width - 10:
                new_text = new_text[:-1]
                break

        rev_text = ""
        for i in range(len(new_text), 0, -1):
            rev_text += new_text[i - 1]

        self.line = rev_text


class Text_container:
    def __init__(self, text: str, coordinate, width: int = 300, height: int = 0,
                 font=font_25, colors=standard, mod: str = "text", vertical: bool = True):
        self.text = Text_vertical(text, width, font, mod) if vertical else Text_horizontal(text, width, font, mod)
        self.coordinate = coordinate
        self.color = colors
        self.size = [width, 55 if height == 0 else height]
        self.hovered = False
        self.active = False
        self.font = font
        self.mod = mod
        self.vertical = vertical
        self.char_number = 0
        if self.vertical:
            self.line_number = self.text.find_line(self.char_number)
        self.number_lines_in_container = self.size[1] // font.get_height()
        self.animation = 0
        self.pressed_button = 0
        if not vertical:
            self.text.split_to_size(self.char_number)

    @property
    def get_text(self):
        return self.text.text

    def set_coordinate(self, coordinate):
        self.coordinate = coordinate

    def hover(self, mouse_pos):
        self.hovered = rect_hover(mouse_pos, self.coordinate, self.size[0], self.size[1])
        return self.hovered

    def draw(self, other_guidance: bool = False):
        draw_rect(self.coordinate, self.size, self.color, self.hovered and not other_guidance, self.active, True)
        if self.vertical:
            vertical_text(self.text.lines, [self.coordinate[0] + 5, self.coordinate[1]],
                          self.number_lines_in_container, self.line_number[0], font=self.font, shift=self.size[0])
            if 0 < self.animation < 15:
                if self.line_number[0] > len(self.text.lines) - self.number_lines_in_container:
                    y = len(self.text.lines) - self.line_number[0] - 1 if len(self.text.lines) > 0 else 0
                else:
                    y = self.number_lines_in_container - 1
                y = self.coordinate[1] + self.font.get_height() * y + 5
                x = list(reversed(self.text.lines))[self.line_number[0]] if len(self.text.lines) > 0 else ""
                x = self.coordinate[0] + 4 + self.font.size(x[:len(x) - self.line_number[1]])[0]
                pygame.draw.rect(screen, black, (x, y, 2, self.font.get_height() - 10))
        else:
            draw_text(self.text.line, [self.coordinate[0] + 5, self.coordinate[1]], font=self.font)
            if 0 < self.animation < 15:
                if self.char_number <= len(self.text.text) - self.text.max_line_number:
                    x = self.coordinate[0] + 4 + self.font.size(self.text.line)[0]
                else:
                    x = self.text.line[: len(self.text.text) - self.char_number]
                    x = self.coordinate[0] + 4 + self.font.size(x)[0]
                pygame.draw.rect(screen, black, (x, self.coordinate[1] + 5, 2, self.font.get_height() - 10))
            y = self.coordinate[1] + self.font.get_height() - 15
            if self.char_number > 0 and self.text.text != self.text.line:
                draw_text("...", [self.coordinate[0] + self.size[0] - font_15.size('...')[0] - 3, y], font=font_15)
            if self.char_number < len(self.text.text) - self.text.max_line_number + 1:
                draw_text("...", [self.coordinate[0] + 3, y], font=font_15)

        self.animation += 1
        if self.animation > 29 or not self.active:
            self.animation = 0

        if self.animation % 3 == 0:
            if self.pressed_button == 2 and self.char_number < len(self.text.text):
                new_text = self.text.text[:len(self.text.text) - self.char_number - 1] + \
                           self.text.text[len(self.text.text) - self.char_number:]
                if self.vertical:
                    self.text.new_text(new_text)
                    self.line_number = self.text.find_line(self.char_number)
                else:
                    self.text.new_text(new_text, self.char_number)
            elif self.pressed_button == 3 and self.char_number > 0:
                new_text = self.text.text[:len(self.text.text) - self.char_number] + \
                           self.text.text[len(self.text.text) - self.char_number + 1:]
                self.char_number -= 1
                if self.vertical:
                    self.text.new_text(new_text)
                    self.line_number = self.text.find_line(self.char_number)
                else:
                    self.text.new_text(new_text, self.char_number)
            elif (self.pressed_button == 1 and self.char_number < len(self.text.text)) or \
                    (self.pressed_button == -1 and self.char_number > 0):
                if self.vertical:
                    self.char_number += self.pressed_button
                    self.line_number = self.text.find_line(self.char_number)
                else:
                    self.char_number += self.pressed_button
                    self.text.split_to_size(self.char_number)
            elif self.vertical:
                if self.press == 4:
                    if self.line_number[0] < len(self.text.lines) - 1:
                        if len(self.text.lines[len(self.text.lines) - self.line_number[0] - 1]) < self.line_number[1]:
                            self.line_number[1] = len(self.text.lines[len(self.text.lines) - self.line_number[0] - 1])
                        self.line_number[0] = self.line_number[0] + 1
                        self.char_number = self.text.find_char_number(self.line_number[0]) + self.line_number[1]
                elif self.press == 5:
                    if self.line_number[0] > 0:
                        if len(self.text.lines[len(self.text.lines) - self.line_number[0] - 1]) < self.line_number[1]:
                            self.line_number[1] = len(self.text.lines[len(self.text.lines) - self.line_number[0] - 1])
                        self.line_number[0] = self.line_number[0] - 1
                        self.char_number = self.text.find_char_number(self.line_number[0]) + self.line_number[1]

    def write(self, event):
        if event.key != pygame.K_TAB:
            new_text = self.text.text[:len(self.text.text) - self.char_number] + str(event.unicode) + \
                       self.text.text[len(self.text.text) - self.char_number:]
            if (self.mod == 'text' or self.mod == 'password') and len(new_text) > 255:
                return
            elif self.mod in ['number', 'year', 'phone'] and not new_text.isdigit():
                return
            elif self.mod == 'number' and int(new_text) >= 9223372036854775807:
                return
            elif self.mod == 'year' and int(new_text) > datetime.date(2023, 8, 2).today().year:
                return
            elif self.mod == 'phone' and len(new_text) > 11:
                return
            if self.vertical:
                self.text.new_text(new_text)
                self.line_number = self.text.find_line(self.char_number)
            else:
                self.text.new_text(new_text, self.char_number)

    def press(self, event):
        if event.type == pygame.KEYUP and \
                (event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_BACKSPACE,
                               pygame.K_DELETE, pygame.K_UP, pygame.K_DOWN]):
            self.pressed_button = 0
        elif event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            if event.button == 1:
                self.active = True
            elif self.vertical:
                if event.button == 4:
                    if self.line_number[0] < len(self.text.lines) - 1:
                        if len(self.text.lines[len(self.text.lines) - self.line_number[0] - 1]) < self.line_number[1]:
                            self.line_number[1] = len(self.text.lines[len(self.text.lines) - self.line_number[0] - 1])
                        self.line_number[0] = self.line_number[0] + 1
                        self.char_number = self.text.find_char_number(self.line_number[0]) + self.line_number[1]
                elif event.button == 5:
                    if self.line_number[0] > 0:
                        if len(self.text.lines[len(self.text.lines) - self.line_number[0] - 1]) < self.line_number[1]:
                            self.line_number[1] = len(self.text.lines[len(self.text.lines) - self.line_number[0] - 1])
                        self.line_number[0] = self.line_number[0] - 1
                        self.char_number = self.text.find_char_number(self.line_number[0]) + self.line_number[1]

        elif (event.type == pygame.KEYDOWN and self.active):
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_LEFT:
                self.pressed_button = 1
            elif event.key == pygame.K_RIGHT:
                self.pressed_button = -1
            elif event.key == pygame.K_BACKSPACE:
                self.pressed_button = 2
            elif event.key == pygame.K_DELETE:
                self.pressed_button = 3
            elif event.key == pygame.K_UP:
                self.pressed_button = 4
            elif event.key == pygame.K_DOWN:
                self.pressed_button = 5
            elif event.mod & pygame.KMOD_CTRL:
                if event.key == pygame.K_c:
                    pyperclip.copy(self.text.text)
                elif event.key == pygame.K_v:
                    new_text = self.text.text[:len(self.text.text) - self.char_number] + pyperclip.paste() + \
                               self.text.text[len(self.text.text) - self.char_number:]
                    if self.vertical:
                        self.text.new_text(new_text)
                        self.line_number = self.text.find_line(self.char_number)
                    else:
                        self.text.new_text(new_text, self.char_number)
            else:
                self.write(event)
        if self.mod == "year" and self.text.text == "0":
            self.text.new_text("")


class Button:
    def __init__(self, text: str, coordinate, width: int = 300, font=font_25, height: int = 0,
                 circle=False, hint="", colors=standard):
        self.text = Text_vertical(text, width, font)
        self.coordinate = coordinate
        self.colors = colors
        self.size = [width, 5 + font.get_height() * len(self.text.lines) if height == 0 else height]
        self.hovered = False
        self.font = font
        self.circle = circle
        self.hint = Text_vertical(hint, 200, font_15) if hint != "" else None

    @property
    def get_text(self):
        return self.text.text

    def hover(self, mouse_pos):
        if not self.circle:
            self.hovered = pygame.Rect(self.coordinate[0], self.coordinate[1], self.size[0], self.size[1])
        else:
            self.hovered = draw_circle(self.coordinate, self.size[0] / 2, self.colors, False)
        self.hovered = self.hovered.collidepoint(mouse_pos[0], mouse_pos[1])
        return self.hovered

    def draw_hint(self, mouse_pos):
        if self.hint and self.hovered:
            x = mouse_pos[0] + 5 if mouse_pos[0] + 205 < screen_size[0] else mouse_pos[0] - 205
            if mouse_pos[1] + 5 + font_15.get_height() * len(self.hint.lines) < screen_size[1]:
                y = mouse_pos[1] + 5
            else:
                y = mouse_pos[1] + 5 + font_15.get_height() * len(self.hint.lines)
            draw_rect_with_border((x, y), 200, font_15.get_height() * len(self.hint.lines))
            vertical_text(self.hint.lines, [x + 100, y], len(self.text.lines) + 1, 0, black, font_15, True)

    def draw(self, other_hovered: bool = False):
        if not self.circle:
            draw_rect(self.coordinate, self.size, self.colors, self.hovered and not other_hovered, False)
        else:
            draw_circle(self.coordinate, self.size[0] / 2, self.colors, self.hovered and not other_hovered)
        x = self.coordinate[0] + self.size[0] / 2
        y = self.coordinate[1]
        if self.circle:
            x -= self.size[0] / 4
            y -= self.size[0] / 4
        vertical_text(self.text.lines, [x, y], len(self.text.lines), 0, black, self.font, True)

    def press(self, event):
        if self.hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.hovered = False
            return True
        return False
