# sudokutools
> Yet another python sudoku library.

```
  5 2 |       | 7 4  
9     | 6   3 |     2
3     |   5   |     8
------+-------+------
  3   |       |   7  
  8   |       |   9  
    5 |       | 8    
------+-------+------
      | 2   4 |      
      |   3   |      
5 4 6 | 9 7 8 | 3 2 1
```

## About
sudokutools is a collection of functions and classes, which enable you
to read, create, analyze, solve and print sudokus.

## Development status
This software is in Alpha. API changes may occur between minor versions.
It should however be quiet stable: Right now its functionality is covered
with 40+ unit tests.

## Installation
sudokutools is available via the Python Package Index (pypi).
Installing and testing can be done with:
```
python -m pip install sudokutools
python -m unittest discover sudokutools -v 
```

## Documentation
You can find the library documentation on readthedocs: <http://sudokutools.readthedocs.io>.

## License
sodukutools is licensed under the MIT-License, which means, you can do pretty
much everything you want with it. For details see ``LICENSE.txt``.

## Features
### Parsing and printing
```python
from sudokutools.sudoku import Sudoku

SUDOKU = """
000030000
005009602
008004013
020060000
703040106
000080090
210300800
306800700
000020000
"""

sudoku = Sudoku.decode(SUDOKU)

print("For machines:")
print(sudoku.encode())

print("For humans:")
print(sudoku)
```

Output:
```
For machines:
000030000005009602008004013020060000703040106000080090210300800306800700000020000
For humans:
      |   3   |      
    5 |     9 | 6   2
    8 |     4 |   1 3
------+-------+------
  2   |   6   |      
7   3 |   4   | 1   6
      |   8   |   9  
------+-------+------
2 1   | 3     | 8    
3   6 | 8     | 7    
      |   2   |      
```

### Calculating candidates
```python
from sudokutools.solve import calc_candidates

# sudoku is the instance from the code above
candidates = calc_candidates(sudoku, 0, 8)
print(candidates)
```

Output:
```
{4, 5, 7, 8, 9}
```

### Solving sudokus
```python
from sudokutools.solve import bruteforce

# sudoku is the instance from the code above
solution = bruteforce(sudoku)
print(solution)
```

Output:
```
1 9 2 | 6 3 8 | 5 7 4
4 3 5 | 7 1 9 | 6 8 2
6 7 8 | 2 5 4 | 9 1 3
------+-------+------
9 2 1 | 5 6 7 | 4 3 8
7 8 3 | 9 4 2 | 1 5 6
5 6 4 | 1 8 3 | 2 9 7
------+-------+------
2 1 9 | 3 7 6 | 8 4 5
3 4 6 | 8 9 5 | 7 2 1
8 5 7 | 4 2 1 | 3 6 9
```

### Creating new sudokus
```python
from sudokutools.generate import generate

sudoku = generate(symmetry="mirror-xy")
print(sudoku)
```

Output:
```
    5 |       | 2    
  6   | 3   2 |   4  
  4   |   9   |   8  
------+-------+------
6     | 1   8 |     9
    1 | 9   5 | 3    
9     | 2   4 |     6
------+-------+------
  7   |   8   |   9  
  1   | 7   3 |   6  
    8 |       | 1    
```

There's much more that you can do, so be sure to check out the documentation.

## Road map and changelog

### Version 0.2 (in development)
#### Features (planned):
* More printing: print the candidates of sudokus
* Different solving strategies, which can be used to learn solving sudokus
* Commandline interface to sudokutools
* Creating sudokus from pattern templates (like the one at the top of the README)

#### Changes:
* **API change:** The method signature of ``Sudoku.remove_candidates()`` in
  the ``sudokutools.sudoku`` module has been changed to be consistent with
  the signature of ``Sudoku.set_candidates()``:

  ```python
  Sudoku.remove_candidates(self, row, col, *candidates)
  Sudoku.remove_candidates(self, row, col, value)
  ```
  You have to change your code, if you used ``Sudoku.remove_candidates()``.


### Version 0.1.1 (current)
#### Changes:
* Added tests to pypi package.
* Minor additional packaging changes.

### Version 0.1
#### Features:
* Parsing and printing sudokus
* Solving using bruteforce
* Calculation of candidates
* Creating new sudokus (supporting various forms of symmetry)
* Checking solutions for correctness
* Checking sudokus for uniqueness

#### Changes:
* Added module ``sudokutools.generate`` for sudoku creation.
* Added module ``sudokutools.solve`` for low-level solving and checks.
* Added module ``sudokutools.sudoku`` for parsing and printing of sudokus
  as well as coordinate calculations. 
* Added ``tests`` for all the modules above.
