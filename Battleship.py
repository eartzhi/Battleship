import random


class TwoCoordinatesException(Exception):

    def __str__(self):
        return 'Вы должны ввести две координаты через пробел.'


class RightCoordinatesException(Exception):

    def __str__(self):
        return 'Одна координата должна быть буквой,'


class OutOfFieldException(Exception):

    def __str__(self):
        return 'Буквы должны быть от А-J, цифры от 1 до 10'


class CoordinateRepeatException(Exception):

    def __str__(self):
        return f'Вы уже стреляли по этой координате'


class Dot:

    def __init__(self, coordinate_x, coordinate_y):
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y

    def __eq__(self, other):
        return self.coordinate_x == other.coordinate_x \
            and self.coordinate_y == other.coordinate_y

    def __str__(self):
        return f'x = {self.coordinate_x}, y = {self.coordinate_y + 1}'


class Ship:

    def __init__(self, lengh):
        self.lengh = lengh
        self.ship_dots = []
        self.round_dots = []
        self.sink = False

    def check_sink(self):
        if not self.ship_dots:
            print(f'**************************\n'
                  f'Корабль длинной {self.lengh} потоплен\n'
                  f'**************************\n')
            self.sink = True

    def set_coordinates(self, start_dot, vert_direction):
        self.ship_dots = []
        self.ship_dots.append(start_dot)
        for i in range(self.lengh - 1):
            if vert_direction:
                self.ship_dots.append(
                    Dot(chr(ord(self.ship_dots[-1].coordinate_x) - 1),
                        self.ship_dots[-1].coordinate_y))
            else:
                self.ship_dots.append(Dot(self.ship_dots[-1].coordinate_x,
                                          self.ship_dots[-1].coordinate_y + 1))
        return self.ship_dots

    def set_round_dots(self):
        self.round_dots = []
        for i in self.ship_dots:
            self.round_dots.append(
                Dot(chr(ord(i.coordinate_x) - 1), i.coordinate_y))
            self.round_dots.append(
                Dot(chr(ord(i.coordinate_x) + 1), i.coordinate_y))
            self.round_dots.append(Dot(i.coordinate_x, i.coordinate_y - 1))
            self.round_dots.append(Dot(i.coordinate_x, i.coordinate_y + 1))
            self.round_dots.append(
                Dot(chr(ord(i.coordinate_x) - 1), i.coordinate_y + 1))
            self.round_dots.append(
                Dot(chr(ord(i.coordinate_x) - 1), i.coordinate_y - 1))
            self.round_dots.append(
                Dot(chr(ord(i.coordinate_x) + 1), i.coordinate_y + 1))
            self.round_dots.append(
                Dot(chr(ord(i.coordinate_x) + 1), i.coordinate_y - 1))
        pop_dots = self.round_dots.copy()
        for i in pop_dots:
            if (i in self.ship_dots) or not (
                    (i.coordinate_x in 'ABCDEFGHIJ')
                    and 0 <= i.coordinate_y <= 9
            ):
                self.round_dots.remove(i)


class Field:

    def __init__(self, name=None, fleet=None):
        self.name = name
        self.fleet = fleet
        self.field = {}
        self.wrong_input = False
        self.free_dots = []

    def create_field(self):
        for i in 'ABCDEFGHIJ':
            self.field[i] = [' '] * 10
            for j in range(10):
                self.free_dots.append((Dot(i, j)))

    def show_field(self):
        print(
            '\n    |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9  |  10')
        print('----------------------------'
              '-----------------------------------')
        for point_x, array_y in self.field.items():
            print(f' {point_x}  ', end='')
            for poin_y in array_y:
                print(f'|  {poin_y}  ', end='')
            print('')
            print('----------------------------'
                  '-----------------------------------')


class FleetField(Field):

    def fleet_set(self):
        count = 0
        for ship in self.fleet:
            no_place = True
            while no_place:
                ship.set_coordinates(Dot(random.choice('ABCDEFGHIJ'),
                                         random.randint(0, 9)),
                                     random.randint(0, 1))
                right_dots_count = 0
                for dot in ship.ship_dots:
                    if dot in self.free_dots:
                        right_dots_count += 1
                if right_dots_count == len(ship.ship_dots):
                    no_place = False
                count += 1
            ship.set_round_dots()
            if not no_place:
                for dot in ship.ship_dots:
                    self.free_dots.remove(dot)
                    self.field[dot.coordinate_x][dot.coordinate_y] = '■'
                for dot in ship.round_dots:
                    if dot in self.free_dots:
                        self.free_dots.remove(dot)
                        self.field[dot.coordinate_x][dot.coordinate_y] = 'O'
        print(f'{self.name} создалось за '
              f'{count} попыток поставить корабль')


class ActionField(Field):

    def take_shot(self, dot, fatal_error):
        hit = False
        if not fatal_error:
            self.free_dots.remove(dot)
            for ship in self.fleet:
                if dot in ship.ship_dots:
                    print('\n-----Попал!!!-----\n')
                    self.field[dot.coordinate_x][dot.coordinate_y] = 'X'
                    ship.ship_dots.remove(dot)
                    ship.check_sink()
                    hit = True
            if not hit:
                print('\n-----Мимо!-----\n')
                self.field[dot.coordinate_x][dot.coordinate_y] = 'О'
        return hit


class Player:

    def __init__(self, fleet1, fleet2, name=''):
        self.name = name
        self.player_field = FleetField(name=f'Поле флота {self.name}',
                                       fleet=fleet1)
        self.enemy_field = ActionField(fleet=fleet2)

    def take_coordinate(self):
        for j in range(5):
            wrong_input = False
            try:
                new_coordinate = input(
                    f'Введите координату для выстрела: \n').upper().split()
                if len(new_coordinate) != 2:
                    wrong_input = True
                    raise TwoCoordinatesException()
                if not all([new_coordinate[0].isalpha(),
                            new_coordinate[1].isdigit()]):
                    wrong_input = True
                    raise RightCoordinatesException()
                new_coordinate = [str.upper(new_coordinate[0]),
                                  int(new_coordinate[1]) - 1]
                if not all([new_coordinate[0] in 'ABCDEFGHIJ',
                            0 <= new_coordinate[1] <= 9]):
                    wrong_input = True
                    raise OutOfFieldException()
                if not (Dot(new_coordinate[0], new_coordinate[1])
                        in self.enemy_field.free_dots):
                    wrong_input = True
                    raise CoordinateRepeatException()
            except TwoCoordinatesException:
                print(TwoCoordinatesException())
                print(f'Осталось {4 - j} попыток\n')
            except RightCoordinatesException:
                print(RightCoordinatesException())
                print(f'Осталось {4 - j} попыток\n')
            except OutOfFieldException:
                print(OutOfFieldException())
                print(f'Осталось {4 - j} попыток\n')
            except CoordinateRepeatException:
                print(CoordinateRepeatException())
                print(f'Осталось {4 - j} попыток\n')
            if not wrong_input:
                return Dot(new_coordinate[0], new_coordinate[1]), wrong_input
        return Dot(None, None), wrong_input

    def take_shot(self):
        shot_coordinate, fatal_error = self.take_coordinate()
        return self.enemy_field.take_shot(shot_coordinate,
                                          fatal_error), fatal_error

    def remove_ship(self):
        for ship in self.enemy_field.fleet:
            if ship.sink:
                for dot in ship.round_dots:
                    if dot in self.enemy_field.free_dots:
                        self.enemy_field.field[dot.coordinate_x][
                            dot.coordinate_y] = 'O'
                        self.enemy_field.free_dots.remove(dot)
                self.enemy_field.fleet.remove(ship)

    def win_check(self):
        if not self.enemy_field.fleet:
            return True


class AIPlayer(Player):

    def take_coordinate(self):
        while True:
            new_coordinate_x = random.choice('ABCDEFGHIJ')
            new_coordinate_y = random.randint(0, 9)
            if Dot(new_coordinate_x,
                   new_coordinate_y) in self.enemy_field.free_dots:
                break
        print(
            f'Компьютер стреляет:\n {Dot(new_coordinate_x, new_coordinate_y)}\n')
        return Dot(new_coordinate_x, new_coordinate_y), False


class Game:

    def __init__(self):
        self.player1 = Player(fleet1=fleet_player1, fleet2=fleet_player2,
                              name='Игрок')
        self.player2 = AIPlayer(fleet1=fleet_player2, fleet2=fleet_player1,
                                name='Компьютер')

    def greetings(self):
        print('**************************************\n'
              '******** ИГРА "МОРСКОЙ БОЙ" **********\n'
              '** координаты вводятся через пробел **\n'
              '**** в формате буква цифра (A 10) ****\n'
              '**************************************\n')

    def preparation(self):
        for player in [self.player1, self.player2]:
            player.player_field.create_field()
            player.enemy_field.create_field()
            player.player_field.fleet_set()
        print(f'\nПоле {self.player1.name} создано\n')
        self.player1.player_field.show_field()
        # self.player2.player_field.show_field()  # Для проверки

    def moves(self):
        fatal_error = False
        win = False
        while not (fatal_error or win):
            for player in [self.player1, self.player2]:
                hit = True
                while hit:
                    print(f'Ходит {player.name}:\n')
                    hit, fatal_error = player.take_shot()
                    player.remove_ship()
                    if fatal_error:
                        print('**********************************\n'
                              'Критическая ошибка ввода координат\n'
                              '**********************************')
                        break
                    win = player.win_check()
                    player.enemy_field.show_field()
                    if win:
                        print('\n****************************')
                        print(f' Выиграл {player.name} '.center(28, '*'))
                        print('****************************')
                        break
                if fatal_error or win:
                    break


fleet_player1 = [Ship(4), Ship(3), Ship(3), Ship(2), Ship(2), Ship(2), Ship(1),
                 Ship(1), Ship(1), Ship(1)]
fleet_player2 = [Ship(4), Ship(3), Ship(3), Ship(2), Ship(2), Ship(2), Ship(1),
                 Ship(1), Ship(1), Ship(1)]

# fleet_player1 = [Ship(2), Ship(2)]  # Для проверки
# fleet_player2 = [Ship(2), Ship(2)]  # Для проверки

game = Game()
game.greetings()
game.preparation()
game.moves()
