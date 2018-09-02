# /bin/python3

# a connecting game for Elias
# based on his crazy ideas for power ups

class GameBoard(object):
    num_rows = 6;
    num_columns = 7;
    gravity = True;
    wraparound = False;

    powerup_shield = False;
    powerup_X = False;
    powerup_bombs = False;

    board = []

    def __init__(self):
        # go by columns then rows
        # things get dropped from the top, right? so select a column and drop
        self.board = [[0 for cell in range(self.num_rows)] for col in range(self.num_columns)]


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
                        # todo try an f string
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
                        # todo try an f string
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


def game_loop(shields=False):
    gb = GameBoard()
    noone_has_won = True
    # TODO get user names?
    
    while noone_has_won:
        # TODO show valid columns
        gb.display()
        # TODO get input for player 1
        # TODO call drop
        # check for winner
        # TODO repeat for player 2


if __name__ == '__main__':

    print("Welcome to Elias' Connect Game")
    act = input("Do you want to play with or without powerups?")

    if act.startswith("t"):
        test_case_diag_corners()
        print(":)")
        # this will throw an exception for no space
        test_case_1()
        
    elif act.startswith("without") or act.startswith("n"):
        game_loop()
    else:
        # TODO which ones?
        game_loop()
        
