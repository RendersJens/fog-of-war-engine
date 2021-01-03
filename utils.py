# position is represented by a tuple of tuples of letters
# "K": own king
# "N": own knight
# "k": other king
# "n": other knight
# " ": empty
# "#": unknown

start_position = ((" "),
                  ("n", "k"),
                  (" ", " ", " ",),
                  ("n", " ", " ", " "),
                  (" ", " ", " ", " ", "K"),
                  (" ", " ", "N", " ", "N", " "))


blind_view = (("#"),
              ("#", "#"),
              ("#", "#", "#"),
              ("#", "#", "#", "#"),
              ("#", "#", "#", "#", "#"),
              ("#", "#", "#", "#", "#", "#"))


def print_position(position):
    print("-"*5)
    for i, row in enumerate(position):
        line = " | ".join(row[:i+1])
        print("|",line,"|")
        if i < 5:
            print("-"*(len(line)+8))
        else:
            print("-"*(len(line)+4))


def in_bounds(coordinate):
    return coordinate[1] <= coordinate[0] and 0 <= coordinate[0] <= 5 and 0 <= coordinate[1] <= 5


def valid_move(position, move, turn=True):
    if turn:
        knight = "N"
        king = "K"
    else:
        knight = "n"
        king = "k"

    begin, end = move
    if not in_bounds(begin) or not in_bounds(end):
        return False

    piece = position[begin[0]][begin[1]]
    capture = position[end[0]][end[1]]

    if not (piece == king or piece == knight):
        return False
    if capture == king or capture ==knight:
        return False
    elif piece == knight:

        #check l_shape
        if abs(begin[0] - end[0]) == 2 and abs(begin[1] - end[1]) == 1:
            return True
        elif abs(begin[0] - end[0]) == 1 and abs(begin[1] - end[1]) == 2:
            return True
        else:
            return False
    elif piece == king:

        #check king move
        if abs(begin[0] - end[0]) <= 1 and abs(begin[1] - end[1]) <= 1 and not begin == end:
            return True
        else:
            return False


def find_piece(position, piece):
    inds = []
    for i, row in enumerate(position):
        for j, square in enumerate(row):
            if square == piece:
                inds.append((i,j))
    return inds


def list_moves(position, turn=True):
    if turn:
        knight = "N"
        king = "K"
    else:
        knight = "n"
        king = "k"

    moves = []

    #king moves
    king_pos = find_piece(position, king)
    if len(king_pos) > 0:
        king_pos = king_pos[0]
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                new_pos = (king_pos[0]+i, king_pos[1]+j)
                if valid_move(position, [king_pos, new_pos], turn):
                    moves.append([king_pos, new_pos])

    #knight moves
    knight_list = find_piece(position, knight)
    for knight_pos in knight_list:
        for i, j in [(-2, 1), (-1, 2), (1, 2), (2, 1), (2,-1), (1,-2), (-1, -2), (-2, -1)]:
            new_pos = (knight_pos[0]+i, knight_pos[1]+j)
            if valid_move(position, [knight_pos, new_pos], turn):
                moves.append([knight_pos, new_pos])

    return moves

def update_position(position, move, turn=True):
    if valid_move(position, move, turn):
        new_position = list(map(list, position))
        begin, end = move
        new_position[end[0]][end[1]] = position[begin[0]][begin[1]]
        new_position[begin[0]][begin[1]] = " "
        return tuple(map(tuple, new_position))
    else:
        print_position(position)
        print(move)
        raise ValueError("invalid move")

def create_view(position, turn=True):
    view = list(map(list,blind_view))
    moves = list_moves(position, turn)
    for begin, end in moves:
        view[begin[0]][begin[1]] = position[begin[0]][begin[1]]
        view[end[0]][end[1]] = position[end[0]][end[1]]
    return tuple(map(tuple,view))