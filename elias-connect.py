# /bin/python3

# a connecting game for Elias, a 5 year old who loves games
# based on his crazy ideas for power ups
# started June 2018

# See helptext for game design detail


class GameBoard(object):
    num_rows = 6
    num_columns = 7
    gravity = True
    wraparound = False

    powerup_shield = False
    powerup_X = False
    powerup_bombs = False

    board = []

    def __init__(self):
        # go by columns then rows
        # things get dropped from the top, right? so select a column and drop
        self.board = [[0 for cell in range(self.num_rows)] for col in range(self.num_columns)]

    help_text = """
    This is basically a 4 in a row connection game with power ups designed by a grade school kid
    The game is a basic 7 columns and 6 rows grid where pieces are dropped one by one from the top.
    Players take turns selecting an available column to drop in a piece of their color.
    However, there are power ups taht can be enabled to make the game more chaotic.
    - Bombs can be dropped instead of a piece and will destroy pieces from a small area where it hits - one below, one right, one left.
    - (TODO) Shields can be placed over a column to block more pieces being dropped for a number of turns.
    - (TODO) A shock can be dropped in a column so when the opponent drops a piece they get shocked.  3 shocks and a player loses a turn.
    - (TODO) Anti gravity - all the columns shift up in the grid, and play continues where pieces are inserted from the bottom.
    There may be future enhancements to add random powerups and pickups.
    """

    def display(self):
        header = ""
        for x in range(self.num_columns):
            header+="+-"
        print(header + "+")
        #print(self.board)
        for rown in range(self.num_rows):
            row_str = " "
            for coln in range(self.num_columns):
                #row_str +=  self.board[coln][rown]
                row_str += f"{self.board[coln][rown]} "
            print(row_str)
        print(header + "+")

    def drop_in(self, col, chip):
        """ drop in the top of a column, falling down to the first empty spot"""
        # TODO: antigravity
        # TODO: bombs
        if (self.board[col][0] != 0):
            raise(Exception(f"no space in column {col}!"))
        for rown in range(1, self.num_rows):
            if self.board[col][rown] != 0:
                self.board[col][rown - 1] = chip
                return
        self.board[col][self.num_rows - 1] = chip

    def drop_bomb(self, col):
        """ Drop a bomb in to a column.
            When it contacts a chip, remove that chip and surrounding chips (left right below)
            If it hits the bottom, just remove left and right """
        # TODO create a booom board to show X where the bombs went off before downward shuffling
        for rown in range(0, self.num_rows - 1):
            if self.board[col][rown] != 0:
                # blow up by replacing with 0
                self.board[col][rown] = 0
                if rown < self.num_rows:
                    self.board[col][rown +1] = 0
                if col > 0:
                    self.board[col-1][rown] = 0
                    self.apply_gravity_to_col(col-1)
                if col < self.num_columns:
                    self.board[col+1][rown] = 0
                    self.apply_gravity_to_col(col+1)
                return
        # hit the bottom, so just try neighbors
        if self.board[col][self.num_rows-1] != 0:
            self.board[col][self.num_rows-1] = 0
        if col > 0:
            self.board[col-1][self.num_rows-1] = 0
            self.apply_gravity_to_col(col-1)
        if col < self.num_columns:
            self.board[col+1][self.num_rows-1] = 0
            self.apply_gravity_to_col(col+1)


    def apply_gravity_to_col(self, col):
        """ Keep it simple, just assume only one gap.  Apply again if more."""
        for rown in range(self.num_rows-1, 1, -1):
            if self.board[col][rown] == 0:
                # swap
                self.board[col][rown] = self.board[col][rown-1]
                self.board[col][rown-1] = 0


    def check_for_winner(self):
        """ horiz, vert, diag from top left, other diag"""
        # horiz
        for rown in range(self.num_rows):
            last_seen = 0
            last_seen_count = 0
            for coln in range(self.num_columns):
                if self.board[coln][rown] == 0:
                    last_seen = 0
                    last_seen_count = 0
                elif self.board[coln][rown] == last_seen:
                    last_seen_count += 1
                    if last_seen_count == 4:
                        # Formatting a winning message
                        return(f"Player {last_seen} wins!")
                else:
                    last_seen = self.board[coln][rown]
                    last_seen_count = 1
        # vert
        for coln in range(self.num_columns):
            last_seen = 0
            last_seen_count = 0
            for rown in range(self.num_rows):
                if self.board[coln][rown] == 0:
                    last_seen = 0
                    last_seen_count = 0
                elif self.board[coln][rown] == last_seen:
                    last_seen_count += 1
                    if last_seen_count == 4:
                        # Formatting a winning message
                        return(f"Player {last_seen} wins!")
                else:
                    last_seen = self.board[coln][rown]
                    last_seen_count = 1            
        
        # from left top
        # reduce the search cycles, but each stop check all 4 cells
        for coln in range(self.num_columns - 3):
            for rown in range(self.num_rows - 3):
                cell = self.board[coln][rown]
                if cell != 0:
                    if cell == self.board[coln + 1][rown + 1] and \
                       cell == self.board[coln + 2][rown + 2] and \
                       cell == self.board[coln + 3][rown + 3]:
                           return(f"Player {cell} wins!!")
        # other diag
        for coln in range(3, self.num_columns):
            for rown in range(self.num_rows - 3):
                cell = self.board[coln][rown]
                if cell != 0:
                    print(f"..checking {coln}{rown} {self.board[coln][rown]} {self.board[coln-1][rown+1]} {self.board[coln - 2][rown + 2]} {self.board[coln - 3][rown + 3]}") 
                    if cell == self.board[coln - 1][rown + 1] and \
                       cell == self.board[coln - 2][rown + 2] and \
                       cell == self.board[coln - 3][rown + 3]:
                           return(f"Player {cell} wins!!")
        # no winner
        return(None)

    def list_open_columns(self):
        """ return a list of column number that are ok """
        open_columns = []
        for coln in range (self.num_columns):
            # not accounting for antigravity yet
            if self.board[coln][0] == 0:
                open_columns.append(coln)
        return(open_columns)


# TODO remove test cases from this module to their own driver script
def test_case_1():
    print()
    print("Running Test Case 1")
    print()
    gb = GameBoard()
    gb.display()
    print(gb.list_open_columns())
    gb.drop_in(3, 1)
    gb.drop_in(3, 2)
    gb.drop_in(4, 1)
    gb.display()
    print(gb.check_for_winner())
    gb.drop_in(3, 1)
    gb.drop_in(3, 1)
    gb.drop_in(3, 1)
    gb.drop_in(3, 1)
    print(gb.list_open_columns())
    gb.display()
    print(gb.check_for_winner())
    # this should fail
    gb.drop_in(3, 1)
    gb.drop_in(3, 1)
    gb.drop_in(3, 1)

def test_case_diag_corners():
    test_case_diag_lbu()
    test_case_diag_ltd()

def test_case_diag_lbu():
    print()
    print("Running Test Case for winning from the left bottom up")
    print()
    
    gb = GameBoard()
    # bottom left up
    gb.drop_in(0, 1)
    gb.drop_in(1, 2)
    gb.drop_in(2, 2)
    gb.drop_in(3, 2)
    gb.drop_in(1, 1)
    gb.drop_in(2, 2)
    gb.drop_in(3, 2)
    gb.drop_in(2, 1)
    gb.drop_in(3, 2)
    gb.display()
    checked = gb.check_for_winner()
    if checked != None:
        print("Test failed, should not have a winner yet!")
    gb.drop_in(3, 1)
    gb.display()
    checked = gb.check_for_winner()
    if checked != None:
        print(checked)
    else:
        print("Test failed! should have found a winner")

def test_case_diag_ltd():
    print()
    print("Running Test Case for winning from the left top down")
    print()
    

    gb = GameBoard()
    # top left down
    gb.drop_in(0, 1)
    gb.drop_in(0, 1)
    gb.drop_in(0, 2) # break
    gb.drop_in(0, 1)
    gb.drop_in(0, 1)
    gb.drop_in(0, 2)
    
    gb.drop_in(1, 2)
    gb.drop_in(1, 2) # break
    gb.drop_in(1, 1)
    gb.drop_in(1, 1)
    gb.drop_in(1, 2)
    
    gb.drop_in(2, 1)
    gb.drop_in(2, 2) # break
    gb.drop_in(2, 1)
    gb.drop_in(2, 2)

    gb.drop_in(3, 1) # break
    gb.drop_in(3, 2)
    gb.display()
    checked = gb.check_for_winner()
    if checked != None:
        print("Test failed, should not have a winner yet!")
    gb.drop_in(3, 2)
    gb.display()
    checked = gb.check_for_winner()
    if checked != None:
        print(checked)
    else:
        print("Test failed! should have found a winner")


def parse_column_input():
    #todo refactor to here
    pass

# return action chosen, validated column to drop
def parse_input(avail_cols):
    # TODO allow input like "d3"
    act = input("Do you want to drop a token(d) or use a powerup (p)? ")

    if act == None or act == "":
        return None, None
    if act.startswith("d"):
        if act[1:].isdigit() and int(act[1:]) in avail_cols:
            return "d", int(act[1:])
        # TODO just convert the input to a number and call a function
        act = input("What column do you choose? ")
        if act == None or act == "":
            return None, None
        if act.isdigit() and int(act) in avail_cols:
            return "d", int(act)
    elif act.startswith("p"):
        if act[1:].isdigit() and int(act[1:]) < GameBoard.num_columns:
            return "p", int(act[1:])
        print("The only powerup is a bomb!")
        act = input(f"What column do you choose? 0-{GameBoard.num_columns} ")
        if act == None or act == "":
            return None, None
        if act.isdigit() and int(act) < GameBoard.num_columns:
            return "p", int(act)

    # invalid input, try again
    return None, None

# TODO have a player object to hold powerup counts
def player_turn(gb, player_number):
    gb.display()
    avail_cols = gb.list_open_columns()
    print(f"  These columns are available {avail_cols}")
    print(f">> Player {player_number} turn <<")
    need_input = True
    while need_input:
        act, col = parse_input(avail_cols)
        if act == "d":
            gb.drop_in(col, player_number)
            need_input = False
        # TODO: handle powerups
        elif act == "p":
            print("BOOOM")
            gb.drop_bomb(col)
            need_input = False
        else:
            print("Invalid input or not implemented yet, please try again.")
        # if act == None, fall through and loop again

def game_loop(shields=False, bombs=False, shocks=False):
    gb = GameBoard()
    noone_has_won = True
    # TODO get user names?
    
    while noone_has_won:        
        player_turn(gb, 1)

        # check for winner
        checked = gb.check_for_winner()
        if checked != None:
            gb.display()
            print(checked)
            print("Thanks for playing!")
            print()
            break

        # repeat for player 2
        player_turn(gb, 2)
        # check for winner
        checked = gb.check_for_winner()
        if checked != None:
            gb.display()
            print(checked)
            print("Thanks for playing!")
            print()
            break


if __name__ == '__main__':

    print("Welcome to Elias' Connect Game")
    act = input("Do you want to play with (y or enter) or without (n) powerups? Or type h for help. ")

    # Secret run tests mode
    if act.startswith("t"):
        test_case_diag_corners()
        print(":)")
        # this will throw an exception for no space
        test_case_1()

    elif act.startswith("h"):
        print(GameBoard.help_text)

    elif act.startswith("without") or act.startswith("n"):
        game_loop()
    else:
        # TODO which ones?
        game_loop(True, True, True)
