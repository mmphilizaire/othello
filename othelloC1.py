seq = [[*range(0,8)],[*range(8,16)],[*range(16,24)],[*range(24,32)],[*range(32,40)],[*range(40,48)],[*range(48,56)],[*range(56,64)],\
[*range(0,64,8)],[*range(1,64,8)],[*range(2,64,8)],[*range(3,64,8)],[*range(4,64,8)],[*range(5,64,8)],[*range(6,64,8)],\
[*range(7,64,8)]]

for x in [*range(1,8)]+[*range(0,64,8)]:
    new = x
    t = [new]
    while new in [*range(64)] and new%8!=7:
        new = new+9
        if new in [*range(64)]:
            t.append(new)
    seq.append(t)

for x in [*range(0,7)]+[*range(7,64,8)]:
    new = x
    t = [new]
    while new in [*range(64)] and new%8!=0:
        new = new+7
        if new in [*range(64)]:
            t.append(new)
    seq.append(t)

lookup = {}
for sq in range(64):
    lookup[sq]=[]
    for x in seq:
        if sq in x:
            index = x.index(sq)
            if index!=(len(x)-1):
                lookup[sq].append(x[index+1:])
            if x.index(sq)!=0:
                lookup[sq].append(x[x.index(sq)-1::-1])
    remove=[]
    for y in lookup[sq]:
        if len(y)<2:
            remove.append(y)
    for x in remove:
        lookup[sq].remove(x)

adjacent = []
for sq in range(64):
    adjs = [sq-9,sq-8,sq-7,sq-1,sq+1,sq+7,sq+8,sq+9]
    if sq%8==0:
        adjs[0]=-1
        adjs[3]=-1
        adjs[5]=-1
    if sq%8==7:
        adjs[2]=-1
        adjs[4]=-1
        adjs[7]=-1
    if sq//8==0:
        adjs[0]=-1
        adjs[1]=-1
        adjs[2]=-1
    if sq//8==7:
        adjs[5]=-1
        adjs[6]=-1
        adjs[7]=-1

    adjacent.append(adjs)

weight={
0:16,1:-4,2:1,3:0.5,4:0.5,5:1,6:-4,7:16,
8:-4,9:-2,10:-0.1,11:-0.2,12:-0.2,13:-0.1,14:-2,15:-4,
16:1,17:-0.1,18:0.5,19:0,20:0,21:0.5,22:-0.1,23:1,
24:0.5,25:-0.2,26:0,27:0,28:0,29:0,30:-0.2,31:0.5,
32:0.5,33:-0.2,34:0,35:0,36:0,37:0,38:-0.2,39:0.5,
40:1,41:-0.1,42:0.5,43:0,44:0,45:0.5,46:-0.1,47:1,
48:-4,49:-2,50:-0.1,51:-0.2,52:-0.2,53:-0.1,54:-2,55:-4,
56:16,57:-4,58:1,59:0.5,60:0.5,61:1,62:-4,63:16,
}

def display(board):
    for sq in range(8):
        print(board[sq*8:sq*8+8])

def opposite(token):
    if token=="x":
        return "o"
    else:
        return "x"

def moves(board,token):
    lm = set()
    enemy = opposite(token)
    holes = [x for x in range(len(board)) if board[x]=="."]
    for hole in holes:
        for seq in lookup[hole]:
            if board[seq[0]]!=enemy: continue
            for pos in seq[1:]:
                if board[pos]==".": break
                if board[pos]==token:
                    lm.add(hole)
    return lm

def heuristicChoice(board,token,possible):
    t = possible.intersection({0,7,56,63})
    if t:
        possible=t
    else:
        best=set()
        #2
        for move in possible:
            if move%8==0 or move%8==7:
                for idx,adj in enumerate([adjacent[move][1],adjacent[move][6]]):
                    while adj!=-1 and adj not in {0,7,56,63}:
                        if idx==0:
                            adj=adjacent[adj][1]
                        if idx==1:
                            adj=adjacent[adj][6]
                    if adj!=1 and adj in {0,7,56,63} and board[adj]==token:
                        best.add(move)
            if move//8==0 or move//8==7:
                for idx,adj in enumerate([adjacent[move][3],adjacent[move][4]]):
                    while adj!=-1 and adj not in {0,7,56,63}:
                        if idx==0:
                            adj=adjacent[adj][3]
                        if idx==1:
                            adj=adjacent[adj][4]
                    if adj!=1 and adj in {0,7,56,63} and board[adj]==token:
                        best.add(move)
        t = possible.intersection(best)
        if t:
            possible=t
        else:
            remove=set()
            #3
            test = [1,8,9,6,14,15,48,49,57,54,55,62]
            corner = [0,7,56,63]
            for idx,move in enumerate(test):
                if move in possible:
                    if board[corner[idx//3]]!=token:
                        remove.add(move)
            if len(remove)<len(possible):
                for move in remove:
                    possible.remove(move)
            remove=set()
            #4
            for move in possible:
                if move%8==0 or move%8==7 or move//8==0 or move//8==7:
                    remove.add(move)
            if len(remove)<len(possible):
                for move in remove:
                    possible.remove(move)

    return(random.choice([*possible]))

def score(board,token):
    score = 0
    for pos in [pos for pos in range(len(board)) if board[pos]==token]:
        score=score+1*weight[pos]
    for pos in [pos for pos in range(len(board)) if board[pos]==opposite(token)]:
        score=score-1*weight[pos]
    return score

def update(board,token,position):
    switch={position}
    enemy = opposite(token)
    for seq in lookup[position]:
        if board[seq[0]]!=enemy: continue
        for pos in seq[1:]:
            if board[pos]==".": break
            if board[pos]==token:
                switch=switch|set(seq[:seq.index(pos)])
                break
    return "".join([board[x] if x not in switch else token for x in range(64)])

def negamaxTerm(board,token,improvable,hardbound):
    lm = moves(board,token)
    if not lm:
        lm = moves(board,opposite(token))
        if not lm:
            return [score(board,token),-3]
        nm=negamaxTerm(board,opposite(token),-hardbound,-improvable)+[-1]
        return [-nm[0]]+nm[1:]
    best = []
    newHB = -improvable
    for move in lm:
        tempBoard=update(board,token,move)
        newT=opposite(token)
        nm = negamaxTerm(tempBoard,newT,-hardbound,newHB)+[move]
        if not best or nm[0]<newHB:
            best = nm
            if nm[0]<newHB:
                newHB=nm[0]
                if -newHB>=hardbound: return [-best[0]]+best[1:]
    return [-best[0]]+best[1:]

import random
import sys
board = sys.argv[1].lower()
token = sys.argv[2].lower()
print(board)
possible = moves(board,token)
print("Legal moves {}".format(possible))
display("".join([board[x] if x not in possible else "*" for x in range(64)]))
print("My heuristic move is {}".format(heuristicChoice(board,token,possible)))

nm = negamaxTerm(board,token,-64,64)
print("negamax returns {} and I chose move {}".format(nm,nm[-1]))
