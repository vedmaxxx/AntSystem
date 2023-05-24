import math
import random
random.seed("lala")
from prettytable import PrettyTable
table = PrettyTable()


# загрузка данных
def loadData(dataCount):
    # M - города, подгружаем как тестовые данные
    global M
    table = open(('Tests/' + str(dataCount) + '.txt'), 'r').readlines()  # считаем из файла все строки
    table = [[int(item) for item in line.split()] for line in table]  # каждую строку разбиваем на числа
    coords = list(map(lambda s: [s[0], s[1], s[2], s[3]], table))
    for i in range(dataCount):
        for j in range(dataCount):
            M[i][j] = math.sqrt((coords[i][1] - coords[j][1]) ** 2 + (coords[i][2] - coords[j][2]) ** 2 + (coords[i][3] - coords[j][3]) ** 2)


# экземпляр класса Agent - муравей
class Agent:

    def __init__(self):
        self.P = [0] * N
        self.N = S.copy()
        self.N.remove(0)
        self.TL = []
        self.T = []
        self.L = 0

    def calculateP(self, i):
        for j in range(N):
            if (i != j and j in self.N): # город i!=j и он в списке разрешенных
                sum = 0
                for l in self.N:    # находим сумму "предпочтительности" всех маршрутов
                    sum = sum + ((tau[i][l] ** alpha) * (heurInf[i][l] ** beta))
                self.P[j] = ((tau[i][j] ** alpha) * (heurInf[i][j] ** beta)) / sum

            else:
                self.P[j] = 0 # в город не попасть, вероятность = 0
    def calculateL(self):
        self.L = 0
        index = 0
        while(index < len(self.T) - 1):
            i = self.T.pop(index)       # удалили из списка, положили в i
            self.T.insert(index, i)     # вернули i в список
            index += 1
            j = self.T.pop(index)
            self.T.insert(index, j)
            self.L += M[i][j]

class EliteAnt(Agent):
    def __init__(self):
        self.P = [0] * N
        # если мы не прогоняем его, а просто добавляем
        # количество проходок кратчайшего маршрута
        self.N = []
        self.TL = []
        self.T = []
        self.L = 0


# инициализация эвристической информации
def initHeurInf(heurInf):
    for i in range(N):
        for j in range(N):
            if(i == j):
                heurInf[i][j] = 0
            else:
                heurInf[i][j] = eps/M[i][j]
# инициализация феромонов
def initTau(tau):
    for i in range(N):
        for j in range(N):
            if(i==j):
                tau[i][j] = 0
            else:
                tau[i][j] = 0.2


# функция выбора города j
def chooseCity(i, agent, Sr):
    agent.calculateP(i)         # высчитываем вероятность, в какой город лучше пойти
    ruletka = [0]               # шкала вероятностей (0 по умолчанию есть)
    indexs = []                 # запомним номера доступных города и свяжем с рулеткой
    u = random.uniform(0, 1)    # случайное число
    sum = 0

    # заполняем рулетку вероятностями и запоминаем индексы путей
    for j in range(len(agent.P)):
        if(agent.P[j] == 0):
            continue
        sum += agent.P[j]
        ruletka.append( sum )
        indexs.append( j )

    # смотрим, куда рандом выпал и возвращаем соотв. индекс города
    for d in range(len(ruletka) - 1):
        if(u > ruletka[d] and u <= ruletka[d + 1] and indexs[d] in Sr):
            return indexs[d]
        else:
            continue

# функция выбора города j
def eliteChooseCity(i, eliteAgent, Sr):
    eliteAgent.calculateP(i)         # высчитываем вероятность, в какой город лучше пойти
    ruletka = [0]               # шкала вероятностей (0 по умолчанию есть)
    indexs = []                 # запомним номера доступных города и свяжем с рулеткой
    sum = 0

    # заполняем рулетку вероятностями и запоминаем индексы путей
    for j in range(len(eliteAgent.P)):
        if(eliteAgent.P[j] == 0):
            continue
        sum += eliteAgent.P[j]
        ruletka.append( sum )
        indexs.append(j)


    # # смотрим, куда рандом выпал и возвращаем соотв. индекс города
    # for d in range(len(ruletka) - 1):
    #     if(u > ruletka[d] and u <= ruletka[d + 1] and indexs[d] in Sr):
    #         return indexs[d]
    #     else:
    #         continue



# наличие ребра в туре
def isEdgeInTour(agent, i, j):
    for d in range(len(agent.T) - 1):
        if agent.T[d] == i and agent.T[d + 1] == j :
            return True
    return False

# считаем феромон, какой остался после муравья прошедшего по ij ребру
def  calculateTau_k(agent, i, j):
    if isEdgeInTour(agent, i, j):   # если ребро принадлежит туру муравья (если муравей проходил по етому ребру)
        return Q / agent.L                                  # возвращаем вклад муравья
    else:
        return 0

# расчет дельта тау
def calculateDeltaTau(agents, elite, i, j):
    deltaTau = 0
    for index in range(m):                                  # перебираем всех муравьев
        deltaTau += calculateTau_k(agents[index], i, j)     # суммируем вклад муравьев на данном ребре
    for index in range(e):
        deltaTau += calculateTau_k(elite[index], i, j)
    return deltaTau

# обновление феромонов на следующую итерацию
def updatePheromones(agents, elite):
    for i in range(N):
        for j in range(N):
            if(i != j):
                deltaTau = calculateDeltaTau(agents, elite, i, j)
                # tau для будущей итерации
                tau[i][j] = PhLevel * tau[i][j] + deltaTau

# # поиск лучшего решения среди всех
# def findBestSolution(agents):
#     solutions = []
#     solutionsLength = []
#     for i in range(m):
#         solutions[i] = agents[i].T
#


# ПАРАМЕТРЫ
eps = 10            # коэффициент эвристической информации
m = 10              # количество агентов на итерации
e = 10               # количество элитных агентов
tmax = 20           # кол-во итераций
dataCount = 50      # рекомендуют задавать tmax = кол-ву городов
Ro = 0.4            # коэффициент испарения феромона
PhLevel = 1 - Ro    # сколько феромона остается
Q =  1.5            # коэффициент вклада агента
alpha = 1           # константа, степень - определяет влияние феромона на выбор след. вершины
beta = 1            # константа, степень - определяет влияние близости на выбор след. вершины


# ВВОД ДАННЫХ
print('Сколько городов берем?')
dataCount = int(input())                            # считывание кол-ва городов
# m = dataCount
# tmax = dataCount
M = [[0]*dataCount for _ in range(dataCount)]       # инициализация матрицы расстояний
loadData(dataCount)                                 # загрузка данных в матрицу расстояний
S = list(range(dataCount))                          # множество городов
N = dataCount
print('Кол-во городов', N)


# ИНИЦИАЛИЗАЦИЯ ФЕРОМОНОВ И БЛИЗОСТИ
tau = [[0] * N for i in range(N)]       # уровень феромона на ребре между городами
initTau(tau)                            # инициализация феромонов
heurInf = [[0] * N for i in range(N)]   # уровень "близости" на ребре между городами
initHeurInf(heurInf)                    # инициализация близости



# ПОИСК
bestL = 999999                  # инициализация переменных
bestSolution = []               # для поиска кратчайшего пути
bestIter = -1                   #
bestAnt = -1                    #

# АЛГОРИТМ
for count in range(tmax):       # пока не выполнен критерий остановки

    # создаем агентов (муравьев)
    agents = []
    for i in range(m):
        agents.append(Agent())

    elites = []
    for i in range(e):
        elites.append(EliteAnt())


    # построение решения
    for k in range(m):          # перебираем каждого агента k принадл. [1..m]
        Sr = S.copy()           # множество городов для итераций

        ant = agents[k]         # задаем агента
        i = 0                   # стартовый город
        ant.TL.append(i)        # добавляем стартовый город в Табу лист
        ant.T.append(i)         # добавляем стартовый город в тур

        Sr.remove(0)
        # сначала агент проходит все города
        while(Sr):
            j = chooseCity(i, ant, Sr)      # ищем город, для которого вероятность перехода максимальная
            ant.TL.append(j)                # добавляем выбранный город j в конец списка
            ant.N.remove(j)                 # убираем город
            Sr.remove(j)                    # удаляем город j из мн-ва городов
            i = j
            ant.T.append(i)     # добавляем выбранный город в тур
            ant.calculateL()    # рассчитываем длину текущего тура

        # поиск лучшего пути
        if (ant.L < bestL):
            bestL = ant.L
            bestSolution = ant.T
            bestIter = count
            bestAnt = k

    # ввод элитных муравьев
    for k in range(e):
        elitistAnt = elites[k]
        elitistAnt.T = bestSolution
        elitistAnt.TL = bestSolution
        elitistAnt.L = bestL
        elitistAnt.N = []
        # i = 0
        # elitistAnt.TL.append(i)
        # ant.T.append(i)  # добавляем стартовый город в тур


    # как только все агенты построили решение, обновляем феромоны
    updatePheromones(agents, elites)

    # вывод первых трех итераций
    if count < 3 :
        print()
        print("Итерация №", count + 1)
        print("Нашли новый минимальный тур!")
        print("Длина тура: ", bestL)
        print("Минимальный тур:", bestSolution)
    # вывод каждой итерации
    # print("Наименьшая длина тура на итерации: ", count + 1, " равен ", bestL)
    # print("Наименьший тур: ", bestSolution)
print()
print()
print("Тур наименьшей длины: ", bestL)
print(bestSolution)