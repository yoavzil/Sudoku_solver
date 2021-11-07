# Yoav Zilbertzan 204429948
# Elya Wygoda 205365901
import sys
import random
import copy
import time


NUMBERS = [1,2,3,4,5,6,7,8,9]

def to_file(things_pass):
    my_file = open('graphs.txt','w')
    for i in things_pass:
        my_file.write(str(i)+ '\n')
    my_file.close()
# class to store sudoku board.
class Board:
    def __init__(self,mother_board, flag):
        if flag == 0:
            self.board_list = copy.deepcopy(mother_board)
            for line in self.board_list:
                temp = line
                for i in range(len(temp)):
                    if temp[i] == 0:
                        #fill rows without duplicates.
                        number = random.choice([j for j in range(1,10) if j not in temp])
                        temp[i] = number
            #calculate score.
            self.score = (self.column_score() * self.matrix_score())

    # calcualte column score, repetitions decrease the score. the maximal score is 81.
    def column_score(self):
        temp_board = copy.deepcopy(self.board_list)
        for i in range(len(self.board_list)):
            for j in range(len(self.board_list[i])):
                temp_board[i][j] = self.board_list[j][i]
        cScore = 0
        for line in temp_board:
            cScore += ((len(list(set(line)))))
        return ((cScore)/81)

# calculate the smaller blocks score.
    def matrix_score(self):
        temp_board = copy.deepcopy(self.board_list)
        answer = []
        for r in range(3):
            for c in range(3):
                block = []
                for i in range(3):
                    for j in range(3):
                        block.append(temp_board[3*r + i][3*c + j])
                answer.append(block)
        cScore = 0
        for line in answer:
            cScore += ((len(list(set(line)))))
        return ((cScore)/81)

    def get_score(self):
        return (self.score)
# update fitness of board.
    def fitness_update(self):
        self.score = self.matrix_score() * self.column_score()

    def __lt__(self, other): 
        if(self.get_score() < other.get_score()): 
            return True
        else: 
            return False
    def __eq__(self, other): 
        if(self.get_score() == other.get_score()): 
            return True
        else: 
            return False

# recombine the two boards that were chosen through competition,
# randomly choose rows and replace the rows of one with the rows of the other.
def recombination(dad, mom):
    son1 = copy.deepcopy(dad)
    son2 = copy.deepcopy(mom)
    already_chosen = []
    for i in range(5):
        swing = random.choice([j for j in range(0,8) if j not in already_chosen])
        already_chosen.append(swing)
        son1.board_list[swing] = copy.deepcopy(mom.board_list[swing])
        son2.board_list[swing] = copy.deepcopy(dad.board_list[swing])
    son1.fitness_update()
    son2.fitness_update()
    return son1, son2
# go through all rows and flip 2 cells around, only if they are not constant.
def mutation(mother_board,child, rate):
    r = random.uniform(0, 1.1)
    while(r > 1):
        r = random.uniform(0, 1.1)
    if (r < rate):
        for i in range(9):
            h = i
            temp = mother_board[h]
            row1,row2 = random.choices([k for k in range(0,9) if temp[k] == 0],weights=None,cum_weights=None,k=2)
            another_temp = child.board_list[h][row1]
            child.board_list[h][row1] = child.board_list[h][row2]
            child.board_list[h][row2] = another_temp
        child.fitness_update()
    return child

# repair columns if you find a duplicate in them, by swapping numbers in a row.
def optimization(mother_board, child, mode):
    child_t = list(map(list, zip(*child.board_list)))
    mother_t = list(map(list, zip(*mother_board)))
    for idx,col in enumerate(child_t):
        if len(set(col)) < len(set(NUMBERS)):
            x = set(col)
            y = set(NUMBERS)
            z = list(y-x)
            for i in range(9):
                if col.count(col[i]) >= 2 and mother_t[idx][i] == 0:
                    for k,j in enumerate(child.board_list[i]):
                        if j in z and mother_board[i][k] == 0:
                            temp = child_t[idx][i]
                            child_t[idx][i] = child_t[k][i]
                            child_t[k][i] = temp
                            i = 9
                            break
    if mode == 3:
        child.board_list = list(map(list, zip(*child_t)))
        child.fitness_update()
    else:
        child_copy = copy.deepcopy(child)
        child_copy.board_list = list(map(list, zip(*child_t)))
        child_copy.fitness_update()
        child.score = child_copy.get_score()

# choose a candidate to go through recombination, the one with higher fitness is preffered
# with 90% chance.
def competition(spec1, spec2):
    score1 = spec1.get_score()
    score2 = spec2.get_score()
    r = random.uniform(0, 1.1)
    while(r > 1): 
        r = random.uniform(0, 1.1)

    if (r < 0.9):
        if score1 > score2:
            return spec1
        else:
            return spec2
    else:
        if score1 > score2:
            return spec2
        else:
            return spec1

#heart of genetic algorithm, create generation, choose elite, do recombinations, mutate and repeat.
def darwin_evolution(gen_size, gen_num, mother_board, mode):
    board_list = []
    best_list = []
    a = 0
    b = 0
    stale = 0
    while b < gen_num:
        if not mode == 2:
            for j in board_list:
                j.fitness_update()
        if a == 0:
            for i in range(gen_size):
                board_list.append(Board(mother_board,0))
        board_list.sort()

        next_gen = []
        for i in range(len(board_list)-1 , len(board_list)-6, -1):
            next_gen.append(board_list[i])
        for i in range(0,gen_size - 5,2):
            s1 = random.choices(board_list,weights=None,cum_weights=None,k=2)
            s2 = random.choices(board_list,weights=None,cum_weights=None,k=2)

            r1 = competition(s1[0], s1[1])
            r2 = competition(s2[0], s2[1])
            
            rec_result = recombination(r1, r2)

            if mode == 1:
                mutation(mother_board,rec_result[0],0.4)
                mutation(mother_board,rec_result[1],0.4)
                next_gen.append(rec_result[0])
                next_gen.append(rec_result[1])
                rec_result = 0

            if mode == 3 or mode == 2:
                o1 = mutation(mother_board,rec_result[0],0.4)
                o2 = mutation(mother_board,rec_result[1],0.4)
                optimization(mother_board, o1, mode)
                optimization(mother_board, o2, mode)
                next_gen.append(o1)
                next_gen.append(o2)
                rec_result = 0

            

        board_list.clear()
        board_list = next_gen
        best = 0
        for i in board_list:
            if best < i.get_score():
                best = i.get_score()
            # if the score is 1 return.
            if i.get_score() >= 1:
                print(b)
                return board_list
        board_list.sort()
        #check if you are stuck.
        if(board_list[len(board_list)-1].get_score() != board_list[len(board_list)-2].get_score()):
            stale = 0
        else:
            stale += 1
        best_list.append(best)
        print(best)
        #if you are stuck more than 100 generations, respawn whole new generation.
        if stale >= 100:
            print(best)
            stale = 0
            a = -1
            next_gen.clear()
            board_list.clear()
        b += 1
        a += 1
    print(b)
    return board_list
    
def main():
    #load board.
    sudoku = open(sys.argv[1], 'r')
    mode = int(sys.argv[2])
    ll = []
    for line in sudoku:
        ll.append([int(x) for x in (list(line.strip('\n').split(' ')))])

    gen_size = 100
    gen_num = 1000
    start = time.time()
    board_list = darwin_evolution(gen_size, gen_num, ll, mode)
    end = time.time()

    #print solved board.
    for c in board_list:
        if c.get_score() >= 1:
            for i in c.board_list:
                print(i)
            break
    print(end - start)


if __name__== "__main__":
  main()