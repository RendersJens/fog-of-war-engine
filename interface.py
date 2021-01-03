from utils import (start_position,
                   update_position,
                   create_view,
                   print_position)
import engine
from tqdm import tqdm
from time_limit import time_limit


ended = False
current_position = start_position
possible = frozenset({start_position})

while not ended:

    # show the current view
    view = create_view(current_position, False)
    print_position(view)

    # take user input
    inp = input("select piece\n")
    begin = tuple(int(i) for i in inp.split(","))
    inp = input("select target\n")
    end = tuple(int(i) for i in inp.split(","))
    user_move = [begin, end]

    # play the user move
    current_position = update_position(current_position, user_move, False)

    # show the current view
    view = create_view(current_position, False)
    print_position(view)

    # update the information of the computer
    computer_view = create_view(current_position, True)
    possible = engine.update_possible(possible, True, computer_view)
    print(len(possible))

    # come up with computer move
    node = engine.Node(view=computer_view, 
                       possible=possible,
                       turn=True)

    try:
        with time_limit(30):
            engine.iterative_deepening(node, 10)
    except TimeoutError as e:
        print("Timed out!")

    print(engine.lookup_table["principal_variation"])
    computer_move = engine.lookup_table["principal_variation"][0]

    # play computer move
    current_position = update_position(current_position, computer_move, True)

    # update the information of the computer
    computer_view = create_view(current_position, True)
    new_possible = set()
    for position in possible:
        new_position = update_position(position, computer_move, True)
        new_possible.add(new_position)
    possible = engine.update_possible(new_possible, False, computer_view)
    print(len(possible))