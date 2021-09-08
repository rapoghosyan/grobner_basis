from PyQt5 import QtWidgets
import sys
import interface
# import time


class Interface(QtWidgets.QMainWindow, interface.Ui_MainWindow):
    an_needed = True

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.comboBox_order_type.addItems(["lex", 'grlex', 'grevlex'])
        # self.comboBox_order_type.activated[str].connect(set_order_type)

        self.lineEdit_variables.setText('x y z')

        self.checkBox_basis_needed.setChecked(True)
        self.checkBox_basis_needed.stateChanged.connect(self.basis_needed_changed)
        self.checkBox_an_needed.setChecked(True)
        self.checkBox_an_needed.stateChanged.connect(self.an_needed_changed)

        self.textEdit_multi_pol.textChanged.connect(self.multi_pol_changed)
        self.lineEdit_pol.textChanged.connect(self.pol_changed)

        self.pushButton_go.clicked.connect(self.go)

        self.textBrowser_basis.setReadOnly(True)
        self.textBrowser_answer.setReadOnly(True)

        self.show_all()
        self.old_multi_pol_list = None
        self.gr_basis = None

    def show_all(self):
        self.label_multi_pol.show()
        self.textEdit_multi_pol.show()
        self.label_pol.show()
        self.lineEdit_pol.show()
        self.label_order_type.show()
        self.comboBox_order_type.show()
        self.label_variables.show()
        self.lineEdit_variables.show()
        self.checkBox_basis_needed.show()
        self.checkBox_an_needed.show()
        self.pushButton_go.show()
        self.label_basis.show()
        self.textBrowser_basis.show()
        self.label_answer.show()
        self.textBrowser_answer.show()

        self.show()

    def basis_needed_changed(self, state):
        if state == 0:
            self.textBrowser_basis.hide()
            self.label_basis.hide()
        else:
            self.textBrowser_basis.show()
            self.label_basis.show()

    def an_needed_changed(self, state):
        if state == 0:
            self.an_needed = False
        else:
            self.an_needed = True

    def go(self):
        global variables, order_type
        changed = False
        variables_0 = variables_to_list(self.lineEdit_variables.text())
        if variables_0 != variables:
            variables = variables_0
            changed = True
        order_type_0 = self.comboBox_order_type.currentText()
        if order_type_0 != order_type:
            order_type = order_type_0
            changed = True
        ok = 1
        multi_pol_list = self.textEdit_multi_pol.toPlainText().split('\n')
        multi_polynomial = Multi_polynomial(multi_pol_list)
        if multi_polynomial.polynomials is None:
            self.textEdit_multi_pol.setStyleSheet("color: rgb(255, 0, 0)")
            ok = 0
        if self.old_multi_pol_list is None or self.old_multi_pol_list != multi_pol_list:
            self.old_multi_pol_list = multi_pol_list
            changed = True

        pol_str = self.lineEdit_pol.text()
        polynomial = Polynomial(pol_str)
        if polynomial.monomials is None:
            self.lineEdit_pol.setStyleSheet("color: rgb(255, 0, 0);")
            ok = 0

        if ok != 0:
            if changed:
                self.gr_basis = multi_polynomial.grobner_basis_fast()
                self.gr_basis.reducing()
                self.textBrowser_basis.clear()
                self.textBrowser_basis.append(self.gr_basis.html_str())
            self.textBrowser_answer.clear()
            if self.an_needed:
                an, r = self.gr_basis.divide(polynomial, True)
                answer = '<sup></sup>'
                answer += polynomial.html_str() + ' = '
                for i in range(an.n):
                    if i != 0:
                        if len(an[i].monomials) == 1 and an[i].monomials[0].coefficient.a < 0:
                            answer += ' -<br>  '
                        else:
                            answer += ' +<br>  + '

                    if len(an[i].monomials) > 1 or\
                            (len(an[i].monomials) == 1 and an[i].monomials[0].coefficient.a < 0):
                        answer += '(' + an[i].html_str() + ') * '
                    else:
                        answer += an[i].html_str() + ' * '

                    if len(self.gr_basis[i].monomials) > 1 or\
                            (len(self.gr_basis[i].monomials) == 1 and self.gr_basis[i].monomials[0].coefficient.a < 0):
                        answer += '(' + self.gr_basis[i].html_str() + ')'
                    else:
                        answer += self.gr_basis[i].html_str()
                if len(r.monomials) == 1 and r.monomials[0].coefficient.a < 0:
                    answer += ' -<br>  '
                else:
                    answer += ' +<br>  + '
                answer += r.html_str() + '<br>'
                self.textBrowser_answer.append(answer)
            else:
                _, r = self.gr_basis.divide(polynomial, False)
            self.textBrowser_answer.append(str(r == Rational(0)))

    def multi_pol_changed(self):
        self.textEdit_multi_pol.setStyleSheet("color: rgb(0, 0, 0)")

    def pol_changed(self):
        self.lineEdit_pol.setStyleSheet("color: rgb(0, 0, 0)")


class Rational:
    """Это класс рациональных чисел"""

    def __init__(self, a: int, b=1):
        self.a = a
        self.b = b
        self.simplify()

    def __str__(self):
        if self.a == 0:
            return '0'
        if self.b == 1:
            return str(self.a)
        return str(self.a) + '/' + str(self.b)

    def __eq__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.a == self.b * other
        else:
            return self.a * other.b == self.b * other.a

    def __add__(self, other):
        ans = Rational(0)
        gcd_bb = gcd(self.b, other.b)
        ans.b = self.b * other.b // gcd_bb
        ans.a = self.a * other.b // gcd_bb + other.a * self.b // gcd_bb
        ans.simplify()
        return ans

    def __sub__(self, other):
        ans = Rational(0)
        gcd_bb = gcd(self.b, other.b)
        ans.b = self.b * other.b // gcd_bb
        ans.a = self.a * other.b // gcd_bb - other.a * self.b // gcd_bb
        ans.simplify()
        return ans

    def __mul__(self, other):
        ans = Rational(0)
        if self.a == 0 or other.a == 0:
            return ans
        ans.a = self.a * other.a
        ans.b = self.b * other.b
        ans.simplify()
        return ans

    def __truediv__(self, other):
        ans = Rational(0)
        if self.a == 0:
            return ans
        if other.a == 0:
            return None
        ans.a = self.a * other.b
        ans.b = self.b * other.a
        ans.simplify()
        return ans

    def __iadd__(self, other):
        return self + other

    def __isub__(self, other):
        return self - other

    def __imul__(self, other):
        return self * other

    def __itruediv__(self, other):
        div = self / other
        if div is not None:
            return self / other
        return self

    def __copy__(self):
        ans = Rational(self.a, self.b)
        return ans

    def simplify(self):
        if self.b < 0:
            self.a *= -1
            self.b *= -1
        sign = 1
        if self.a < 0:
            sign = -1
            self.a *= -1

        gcd_ab = gcd(self.a, self.b)
        self.a //= gcd_ab
        self.a *= sign
        self.b //= gcd_ab


class Monomial:
    """
    Это класс мономов, в нем будут следующие параметры:
        self.coefficient - единственное целое число, коэффициент монома
        self.degrees - список степеней переменных
    """

    def __init__(self, mon_str: str):
        global variables, order_type

        if len(mon_str) == 0:
            self.degrees = None
        else:
            int_ = find_int(mon_str, 0)
            len_verified = 0
            if int_ is None:
                self.coefficient = Rational(1)
                if len(mon_str) != 0 and mon_str[0] == '-':
                    self.coefficient.a *= -1
                    len_verified += 1
            else:
                self.coefficient = Rational(int_)
                len_verified += len(str(int_))

            self.degrees = [0] * len(variables)
            n = len(mon_str)
            for i in range(len(variables)):
                j = mon_str.find(variables[i])
                if j != -1:
                    self.degrees[i] = 1
                    len_var = len(variables[i])
                    len_verified += len_var
                    j += len_var
                    if j < n and mon_str[j] == '^':
                        len_verified += 1
                        j += 1
                    if j < n:
                        degree = find_int(mon_str, j)
                        if degree is None:
                            if mon_str[j-1] == '^':
                                self.degrees = None
                                break
                        else:
                            self.degrees[i] = degree
                            len_verified += len(str(degree))
            if len_verified != len(mon_str):
                self.degrees = None

    # моном > моном не учитывая коэффициенты
    def __gt__(self, other):
        if order_type == 'lex':
            return self.lex(other)
        elif order_type == "grlex":
            return self.grlex(other)
        elif order_type == "grevlex":
            return self.grevlex(other)

    # моном == число или моном == моном без учёта коэффициентов
    def __eq__(self, other):
        global variables, order_type

        if isinstance(other, Rational):
            return self.coefficient == other and sum(self.degrees) == 0
        elif isinstance(other, Monomial):
            for i in range(len(variables)):
                if self.degrees[i] != other.degrees[i]:
                    return False
            return True

    # моном / моном
    def __truediv__(self, other):
        global variables, order_type

        # возвращает None, если не делится, или ответ
        if other.coefficient == 0:
            return None
        ans = Monomial('1')
        for i in range(len(variables)):
            ans.degrees[i] = self.degrees[i] - other.degrees[i]
            if ans.degrees[i] < 0:
                return None
        ans.coefficient = self.coefficient / other.coefficient
        return ans

    # моном * моном
    def __mul__(self, other):
        global variables, order_type

        ans = Monomial('1')
        ans.coefficient = self.coefficient * other.coefficient
        for i in range(len(variables)):
            ans.degrees[i] = self.degrees[i] + other.degrees[i]
        return ans

    def __copy__(self):
        ans = Monomial('1')
        ans.coefficient = self.coefficient.__copy__()
        ans.degrees = self.degrees.copy()
        return ans

    def __str__(self):
        global variables, order_type

        ans = ''
        if self.coefficient == -1:
            ans += '-'
            if sum(self.degrees) == 0:
                ans += '1'
        elif self.coefficient != 1:
            ans += self.coefficient.__str__()
        elif sum(self.degrees) == 0:
            ans += '1'
        for i in range(len(variables)):
            if self.degrees[i] != 0:
                ans += variables[i]
                if self.degrees[i] != 1:
                    ans += '^' + str(self.degrees[i])
        return ans

    def html_str(self):
        global variables, order_type

        ans = ''
        if self.coefficient == -1:
            ans += '-'
            if sum(self.degrees) == 0:
                ans += '1'
        elif self.coefficient != 1:
            ans += self.coefficient.__str__()
        elif sum(self.degrees) == 0:
            ans += '1'
        for i in range(len(variables)):
            if self.degrees[i] != 0:
                ans += variables[i]
                if self.degrees[i] != 1:
                    ans += '<sup>' + str(self.degrees[i]) + '</sup>'
        return ans

    # лексикографическое упорядочение
    def lex(self, other):
        for i in range(len(self.degrees)):
            if self.degrees[i] > other.degrees[i]:
                return True
            elif self.degrees[i] < other.degrees[i]:
                return False
        return False

    # градуированное лексикографическое упорядочение
    def grlex(self, other):
        sum_of_degrees_1 = sum(self.degrees)
        sum_of_degrees_2 = sum(other.degrees)
        if sum_of_degrees_1 > sum_of_degrees_2:
            return True
        elif sum_of_degrees_1 < sum_of_degrees_2:
            return False
        return self.lex(other)

    # градуированное обратное лексикографическое упорядочение
    def grevlex(self, other):
        sum_of_degrees_1 = sum(self.degrees)
        sum_of_degrees_2 = sum(other.degrees)
        if sum_of_degrees_1 > sum_of_degrees_2:
            return True
        elif sum_of_degrees_1 < sum_of_degrees_2:
            return False
        for i in range(len(self.degrees)-1, -1, -1):
            if self.degrees[i] < other.degrees[i]:
                return True
            elif self.degrees[i] > other.degrees[i]:
                return False
        return False


class Polynomial:
    """
    Это класс полиномов, в нем хранятся мономы
    Для этого класса перегружены арифметические операторы
    """

    def __init__(self, pol_str: str):
        # pol_str --> '2x-y+1'
        self.monomials = []

        if len(pol_str) != 0:
            a = pol_str.replace(' ', '').split('-')
            if a[0] != '':
                for elem in a[0].split('+'):
                    self.monomials.append(Monomial(elem))
                    if self.monomials[-1].degrees is None:
                        self.monomials = None
                        break
            if self.monomials is not None:
                for i in range(1, len(a)):
                    for elem in ('-' + a[i]).split('+'):
                        self.monomials.append(Monomial(elem))
                        if self.monomials[-1].degrees is None:
                            self.monomials = None
                            break
                    if self.monomials is None:
                        break
                else:
                    self.simplify()
        else:
            self.monomials = None

    # полином > полином не учитывая коэффициенты
    def __gt__(self, other):
        return self.lt() > other.lt()

    # полином - полином
    def __sub__(self, other):
        ans = self.__copy__()
        for i in range(len(other.monomials)):
            ans.monomials.append(other.monomials[i].__copy__())
            ans.monomials[-1].coefficient.a *= -1
            ans.simplify()
        return ans

    # полином -= полином
    def __isub__(self, other):
        for i in range(len(other.monomials)):
            self.monomials.append(other.monomials[i].__copy__())
            self.monomials[-1].coefficient.a *= -1
            self.simplify()
        return self

    # полином * моном
    def __mul__(self, other: Monomial):
        ans = Polynomial('0')
        for i in range(len(self.monomials)):
            ans.monomials.append(self.monomials[i] * other)
        ans.simplify()
        return ans

    def __eq__(self, i: Rational):
        return (i == 0 and len(self.monomials) == 0) or (len(self.monomials) == 1 and self.monomials[0] == i)

    def __copy__(self):
        ans = Polynomial('0')
        ans.monomials.clear()
        for i in range(len(self.monomials)):
            ans.monomials.append(self.monomials[i].__copy__())
        return ans

    def __str__(self):
        ans = ''
        for i in range(len(self.monomials)):
            if i != 0 and self.monomials[i].coefficient.a >= 0:
                ans += '+'
            ans += self.monomials[i].__str__()
        return ans

    def html_str(self):
        ans = ''
        for i in range(len(self.monomials)):
            if i != 0 and self.monomials[i].coefficient.a >= 0:
                ans += '+'
            ans += self.monomials[i].html_str()
        return ans

    def lt(self):
        self.simplify()
        return self.monomials[0]

    def simplify(self):
        self.monomials.sort(reverse=True)  # знак '>' для мономов перегружен
        for i in range(len(self.monomials) - 1, -1, -1):
            if i+1 < len(self.monomials) and self.monomials[i].degrees == self.monomials[i+1].degrees:
                self.monomials[i].coefficient += self.monomials.pop(i + 1).coefficient
            if self.monomials[i].coefficient == 0:
                self.monomials.pop(i)
        if len(self.monomials) == 0:
            self.monomials.append(Monomial('0'))


class Multi_polynomial:
    """
    Это класс множества полиномов
    """
    def __init__(self, list_str: list[str]):
        self.polynomials = []
        self.n = 0
        for pol_str in list_str:
            self.polynomials.append(Polynomial(pol_str))
            if self.polynomials[-1].monomials is None:
                self.polynomials = None
                break
        else:
            self.n = len(self.polynomials)
            self.b = {}
            if self.n == 0:
                self.polynomials = None

    def __getitem__(self, key):
        return self.polynomials[key]

    def __setitem__(self, key, other: Polynomial):
        self.polynomials[key] = other

    def __copy__(self):
        ans = Multi_polynomial(['0'])
        ans.polynomials.clear()
        for i in range(self.n):
            ans.polynomials.append(self.polynomials[i].__copy__())
        ans.n = self.n
        ans.b = self.b.copy()
        return ans

    def __str__(self):
        ans = ''
        for i in range(self.n):
            ans += self[i].__str__()
            if i != self.n - 1:
                ans += '\n'
        return ans

    def html_str(self):
        ans = '<sup></sup>'
        for i in range(self.n):
            ans += self[i].html_str()
            if i != self.n - 1:
                ans += '<br>'
        return ans

    def simplify(self):
        for i in range(self.n):
            self[i].simplify()

    def sort(self, sort_type=False):
        self.polynomials.sort(reverse=sort_type)

    # алгоритм деления
    def divide(self, f: Polynomial, an_needed):
        f_buf = f.__copy__()
        f_buf.simplify()
        fn = self.__copy__()
        an = Multi_polynomial(['0']*fn.n)
        r = Polynomial('0')

        while f_buf != Rational(0):
            for i in range(fn.n):
                div = f_buf.lt() / fn[i].lt()
                if div is not None:
                    if an_needed:
                        an[i].monomials.append(div)
                    f_buf -= (fn[i] * div)
                    break
            else:
                r.monomials.append(f_buf.monomials.pop(0))
        if an_needed:
            an.simplify()
        r.simplify()

        if an_needed:
            return an, r
        else:
            return None, r

    # S-полином от полиномов f_i и f_j
    def s_pol(self, i, j):
        lcm_ij = lcm(self[i].lt(), self[j].lt())
        return self[i] * (lcm_ij / self[i].lt()) - self[j] * (lcm_ij / self[j].lt())

    # S-полином от полиномов f_i и f_j, но уже LCM(LT(f_i), LT(f_j)) посчитан
    def s_pol_fast(self, lcm_ij: Monomial, i, j):
        return self[i] * (lcm_ij / self[i].lt()) - self[j] * (lcm_ij / self[j].lt())

    # алгоритм Бухбергера
    def grobner_basis(self):
        self.simplify()
        gn = self.__copy__()
        added = 1
        while added == 1:
            added = 0
            for i in range(gn.n - 1):
                for j in range(i + 1, gn.n):
                    _, r = gn.divide(gn.s_pol(i, j), False)
                    if r != Rational(0):
                        gn.polynomials.append(r)
                        gn.n += 1
                        added = 1
        return gn

    # усовершенствованный алгоритм Бухбергера
    def grobner_basis_fast(self):
        self.simplify()
        self.sort()
        gn = self.__copy__()
        t = gn.n
        gn.b = {'-1': [Monomial('1'), '-2']}
        for i in range(t - 1):
            for j in range(i + 1, t):
                lcm_ij = lcm(gn[i].lt(), gn[j].lt())
                if lcm_ij.degrees != (gn[i].lt() * gn[j].lt()).degrees:
                    gn.add_item(str(i) + '_' + str(j), lcm_ij)
        """
        b это словарь, где ключом является 'i_j',а значением - список из 2 элеменов:
          1) LCM(LT(f_i), LT(f_j))
          2) [i_1, j_1]
        тут i_1, j_1 такые, что LCM(LT(f_i), LT(f_j)) <= LCM(LT(f_i_1), LT(f_j_1))
        это нужно для того, чтобы добавить очередную пару и сохранить сортировку
        При добавлении пар мы уже проверяем условые LCM(LT(f_i), LT(f_j)) != LT(f_i) * LT(f_j)
        """
        after_item = gn.b['-1'][1]
        while after_item != '-2':

            i_, j_ = after_item.split('_')
            i, j = int(i_), int(j_)

            if not gn.criterion(i, j):
                _, r = gn.divide(gn.s_pol_fast(gn.b[after_item][0], i, j), False)
                gn.b['-1'][1] = gn.b.pop(after_item)[1]
                if r != Rational(0):
                    gn.polynomials.append(r)
                    for k in range(t):
                        lcm_kt = lcm(gn[k].lt(), gn[t].lt())
                        if lcm_kt.degrees != (gn[k].lt() * gn[t].lt()).degrees:
                            gn.add_item(str(k) + '_' + str(t), lcm_kt)
                    t += 1
                    gn.n += 1
            else:
                gn.b['-1'][1] = gn.b.pop(after_item)[1]
            after_item = gn.b['-1'][1]
        return gn

    # добавляем пару item в список B
    def add_item(self, item: str, lcm_item):
        before_item = '-1'
        after_item = self.b[before_item][1]
        while after_item != '-2' and self.b[after_item][0] < lcm_item:
            before_item = after_item
            after_item = self.b[after_item][1]
        self.b[item] = [lcm_item, after_item]
        self.b[before_item][1] = item

    # критерий (f_i, f_j, B)
    def criterion(self, i, j):
        for l in range(i):
            if str(l) + '_' + str(i) not in self.b and \
                    str(j) + '_' + str(l) not in self.b and \
                    self.b[str(i) + '_' + str(j)][0] / self[l].lt() is not None:
                return True
        for l in range(i + 1, j):
            if str(i) + '_' + str(l) not in self.b and \
                    str(l) + '_' + str(j) not in self.b and \
                    self.b[str(i) + '_' + str(j)][0] / self[l].lt() is not None:
                return True
        for l in range(j + 1, self.n):
            if str(i) + '_' + str(l) not in self.b and \
                    str(j) + '_' + str(l) not in self.b and \
                    self.b[str(i) + '_' + str(j)][0] / self[l].lt() is not None:
                return True
        return False

    # редуцирование базиса Грёбнера
    def reducing(self):
        # построим минимальный базис Грёбнера
        for i in range(self.n):
            _const = self[i].lt().coefficient
            for j in range(len(self[i].monomials)):
                self[i].monomials[j].coefficient /= _const
        for i in range(self.n-1, -1, -1):
            for j in range(self.n-1, -1, -1):
                if i != j:
                    if self[i].lt() / self[j].lt() is not None:
                        self.polynomials.pop(i)
                        self.n -= 1
                        break

        # построим наилучший минимальный базис Грёбнера
        i = 0
        while i < self.n:
            buf = self.__copy__()
            gn_i = buf.polynomials.pop(i)
            buf.n -= 1
            _, r = buf.divide(gn_i, False)
            if r == Rational(0):
                self.polynomials.pop(i)
                self.n -= 1
            else:
                self[i] = r.__copy__()
                i += 1
        self.sort(True)

    # принадлежание идеалу
    def ideal_membership(self, f: Polynomial):
        gn = self.grobner_basis_fast()
        _, r = gn.divide(f, False)
        return r == Rational(0)


# наибольший общий делитель двух натуральних чисел
def gcd(a: int, b: int):
    while a != 0 and b != 0:
        if a > b:
            a = a % b
        else:
            b = b % a
    return a + b


# создаем список переменных
def variables_to_list(variables_: str):
    # variables0 = 'int'         => x1 > x2 > ... > x_int -> ['x1', 'x2', 'x2', ..., 'x_int']
    # variables0 = 'zp x1 y ...' => zp > x1 > y > ...     -> ['zp', 'x1', 'y', ...]

    variables_list = []
    if variables_.isdigit():
        for i in range(1, int(variables_) + 1):
            variables_list.append('x' + str(i))
    else:
        variables_list = variables_.split()

    return variables_list


# ищет число в строке начиная с определённой позиции
def find_int(_str, i):
    n = len(_str)
    if i >= n:
        return None
    sign = 1
    if _str[i] == '-':
        sign = -1
        i += 1
    if i >= n or not _str[i].isdigit():
        return None
    _int = int(_str[i])
    i += 1
    while i < n and _str[i].isdigit():
        _int = _int * 10 + int(_str[i])
        i += 1
    return _int * sign


# наименьшее общее кратное двух мономов не учитывая коэффициенты
def lcm(a: Monomial, b: Monomial):
    global variables, order_type

    ans = Monomial('1')
    for i in range(len(variables)):
        ans.degrees[i] = max(a.degrees[i], b.degrees[i])
    return ans


def set_order_type(key):
    global order_type
    order_type = key


"""
variables - список переменных в правильном порядке
order_type - тип упорядочения мономов('lex', 'grlex', 'grevlex')
"""
variables = variables_to_list('x y z w')
order_type = 'lex'
interface = True

if interface:
    app = QtWidgets.QApplication(sys.argv)
    window = Interface()
    sys.exit(app.exec_())
else:
    f_1 = Polynomial('x')
    my_list = [['x^3-2xy', 'x^2y-2y^2+x'],
               ['3x-6y-2z', '2x-4y+4w', 'x-2y-z-w'],
               ['x^5+y^4+z^3-1', 'x^3+y^2+z^2-1']]
    number = 0
    my_multi_polynomial = Multi_polynomial(my_list[number])
    basis = my_multi_polynomial.grobner_basis_fast()
    basis.reducing()
    print(basis)
    for elem_ in my_multi_polynomial.polynomials:
        _, r_ = basis.divide(elem_, False)
        print(r_)
