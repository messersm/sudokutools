def pretty_str(sudoku):
    s = ""
    for row in range(9):
        for line in range(3):
            for col in range(9):
                if sudoku[row][col] == 0:
                    # add candidates
                    for c in range(line*3 + 1, line * 3 + 4):
                        if c in sudoku.candidates[row][col]:
                            s += "%d" % c
                        else:
                            s += " "
                        if c % 3 != 0:
                            s += " "
                else:
                    if line == 1:
                        s += "  %d  " % sudoku[row][col]
                    else:
                        s += "     "
                if col % 3 == 2 and col < 8:
                    s += "#"
                elif col < 8:
                    s += "|"
            s += '\n'

        if row % 3 == 2 and row < 8:
            s += "#" * (9 * 5 + 8)
            s += '\n'
        elif row < 8:
            s += "-" * (9 * 5 + 8)
            s += '\n'

    return s
