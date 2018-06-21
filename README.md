# sudokutools [![Build Status](https://travis-ci.org/messersm/sudokutools.svg?branch=master)](https://travis-ci.org/messersm/sudokutools) [![Coverage Status](https://coveralls.io/repos/github/messersm/sudokutools/badge.svg)](https://coveralls.io/github/messersm/sudokutools)

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

## Table of contents
* [About](#about)
* [Development status](#development-status)
* [Installation](#installation)
* [Documentation](#documentation)
* [License](#license)
* [Examples](#examples)
* [Sudoku in the Shell](#sudoku-in-the-shell)
* [Road map and changelog](#road-map-and-changelog)

## About
sudokutools is a collection of functions and classes, which enable you
to read, create, analyze, solve and print sudokus written in Python. It
also comes with a commandline tool (the sudokutools shell) named
``sudokutools``.

## Development status
This software is in Alpha. API changes may occur between minor versions.
It should however be quite stable: Right now its functionality is covered
with 60+ unit tests.

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

## Examples
+ [Parsing and printing](#parsing-and-printing)
+ [Printing sudokus with candidates](#printing-sudokus-with-candidates)
+ [Calculating candidates](#calculating-candidates)
+ [Checking sudokus](#checking-sudokus)
+ [Solving sudokus](#solving-sudokus)
+ [Creating new sudokus](#creating-new-sudokus)
+ [Creating sudokus from templates](#creating-sudokus-from-templates)
+ [Different sudoku sizes](#different-sudoku-sizes)

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

### Printing sudokus with candidates
```python
from sudokutools.solve import init_candidates
from sudokutools.sudoku import view

# sudoku is the instance from the code above
init_candidates(sudoku)
print(view(sudoku))
```

Output:
```
  *1469   *4679  *12479 |  *12567       3 *125678 |    *459   *4578  *45789
    *14    *347       5 |     *17     *17       9 |       6    *478       2
    *69    *679       8 |   *2567     *57       4 |     *59       1       3
------------------------+-------------------------+------------------------
 *14589       2    *149 |   *1579       6   *1357 |    *345  *34578   *4578
      7    *589       3 |    *259       4     *25 |       1    *258       6
  *1456    *456     *14 |   *1257       8  *12357 |   *2345       9    *457
------------------------+-------------------------+------------------------
      2       1    *479 |       3    *579    *567 |       8    *456    *459
      3    *459       6 |       8    *159     *15 |       7    *245   *1459
  *4589  *45789    *479 | *145679       2   *1567 |   *3459   *3456   *1459
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

### Checking sudokus
Sudokus are required to have only one solutions, which can be checked using
``sudokutools.solve.is_unique()``. You can also count the number of solutions
using ``sudokutools.solve.bruteforce()``.
Do note, that ``is_unique()`` is much faster than counting the number of
solutions, since it returns after finding two solutions.

```python
from sudokutools.solve import bruteforce, is_unique, find_conflicts
from sudokutools.sudoku import Sudoku

SUDOKU = """
000000006
002040007
090100008
700200000
000070900
189006000
050000030
000000800
000032140
"""

sudoku = Sudoku.decode(SUDOKU)
print(is_unique(sudoku))
print("This sudoku has %d solutions." % len(list(bruteforce(sudoku))))
```

Output:
```
False
This sudoku has 1540 solutions.
```

Finding conflicts can be done using ``sudokutools.solve.find_conflicts()``
which iterates through all fields containing conflicts, yielding the two
conflicting fields as well as the conflicting number:

```python
from sudokutools.solve import find_conflicts
from sudokutools.sudoku import Sudoku

SUDOKU_WITH_CONFLICTS = """
020000006
002040007
090100008
700200000
000070900
189006000
050000030
000000800
300032140
"""

sudoku = Sudoku.decode(SUDOKU_WITH_CONFLICTS)
for conflict in find_conflicts(sudoku):
    print(conflict)
```

Output:
```
((0, 1), (1, 2), 2)
((1, 2), (0, 1), 2)
((8, 0), (8, 4), 3)
((8, 4), (8, 0), 3)
```

### Solving sudokus
sudokutools comes with two modules for solving sudokus. The
``sudokutools.solve`` module provides some low-level functions that
simply get the job done. ``sudokutools.solvers`` provides a more
fine-graded approach to solving sudokus.

```python
from sudokutools.solve import bruteforce

# sudoku is the instance from the code above
# bruteforce() iterates through all possible solutions.
for solution in bruteforce(sudoku):
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

If you want to use a specific solving method you can use the ones provided
by ``sudokutools.solvers``. Since most solving methods depend on the
candidates of fields, these must be calculated first, using the
``CalculateCandidates`` method (which basically does the same as the
``init_candidates()`` function from ``sudokutools.solve`` but provides
more metadata on the actions that are executed).

```python
from sudokutools.solvers import CalculateCandidates, HiddenSingle
from sudokutools.sudoku import Sudoku

SUDOKU = """
400305020
908010000
000000000
003000062
500020000
080700000
700000500
005003004
000408103
"""

sudoku = Sudoku.decode(SUDOKU)
# Candidates must always been calculated first.
CalculateCandidates.apply_all(sudoku)

for step in HiddenSingle.find(sudoku):
    print(step)
    step.apply(sudoku)

print("")
print(sudoku)
```

Output:
```
HiddenSingle at (2, 0): 3
HiddenSingle at (3, 3): 5
HiddenSingle at (5, 4): 3
HiddenSingle at (6, 1): 3
HiddenSingle at (6, 2): 4
HiddenSingle at (7, 0): 8
HiddenSingle at (7, 1): 1
HiddenSingle at (7, 6): 2
HiddenSingle at (8, 4): 5
HiddenSingle at (8, 7): 7

4     | 3   5 |   2  
9   8 |   1   |      
3     |       |      
------+-------+------
    3 | 5     |   6 2
5     |   2   |      
  8   | 7 3   |      
------+-------+------
7 3 4 |       | 5    
8 1 5 |     3 | 2   4
      | 4 5 8 | 1 7 3
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

### Creating sudokus from templates
So you want to draw your favorite animal as sudoku?
Then you have give the ``generate_from_template()`` function a try:

```python
from sudokutools.generate import generate_from_template
from sudokutools.sudoku import Sudoku

CAT = """
110000011
101000101
100111001
111000111
111000111
100000001
010010010
001000100
000111000
"""

template = Sudoku.decode(CAT)
sudoku = generate_from_template(template, tries=-1)
print(sudoku)
```

Output:
```
5 9   |       |   2 7
7   2 |       | 9   1
3     | 9 7 2 |     5
------+-------+------
8 5 3 |       | 1 9 2
1 2 7 |       | 6 3 4
4     |       |     8
------+-------+------
  8   |   3   |   5  
    1 |       | 2    
      | 6 8 7 |      
```

### Different sudoku sizes
``sudokutools`` supports different sizes for sudokus. All methods and
function, which generate or parse sudokus are able to work with them.
In the ``sudokutools`` library "size" always refers to the size of a single
region. That means, standard sudokus have a size of 3x3.

```python
from sudokutools.sudoku import Sudoku

EXAMPLE_16x16 = """
0 4 9 6 1 0 12 0 8 0 14 0 0 0 2 3
0 5 0 7 3 2 8 16 9 0 15 11 12 10 4 13
0 8 0 15 0 0 10 11 2 5 1 0 16 6 9 7
10 11 2 3 7 9 6 15 13 16 0 0 0 0 8 0
7 0 5 14 8 6 0 12 15 2 3 0 1 11 0 9
8 16 1 4 0 7 15 14 0 13 11 0 3 12 6 2
15 3 11 13 2 1 5 10 6 9 0 7 4 16 14 0
9 12 6 2 13 11 0 4 14 1 8 16 0 5 10 15
0 14 7 9 15 12 0 0 11 0 10 2 8 0 16 6
0 2 15 8 10 16 1 0 12 4 0 13 9 3 11 0
11 1 10 12 6 0 13 9 16 8 7 14 2 4 0 5
0 6 3 16 14 8 11 2 0 15 9 1 13 0 0 10
2 7 16 0 11 4 14 0 1 10 13 9 15 8 3 12
0 15 4 1 0 13 7 8 3 0 2 6 10 9 5 0
3 13 12 10 16 15 9 1 4 14 5 8 6 2 7 11
6 9 8 0 0 10 2 0 7 12 16 0 14 13 1 4
"""

sudoku = Sudoku.decode(EXAMPLE_16x16, number_sep=" ")
print(sudoku.size)
print(sudoku)
```

``Sudoku.decode()`` also provides a ``size`` keyword argument, which can
be used, if the size of a region in the sudoku is arbitrary (e.g. 2x3 or 3x2).

Output:
```
(4, 4)
    4  9  6 |  1    12    |  8    14    |        2  3
    5     7 |  3  2  8 16 |  9    15 11 | 12 10  4 13
    8    15 |       10 11 |  2  5  1    | 16  6  9  7
10 11  2  3 |  7  9  6 15 | 13 16       |        8   
------------+-------------+-------------+------------
 7     5 14 |  8  6    12 | 15  2  3    |  1 11     9
 8 16  1  4 |     7 15 14 |    13 11    |  3 12  6  2
15  3 11 13 |  2  1  5 10 |  6  9     7 |  4 16 14   
 9 12  6  2 | 13 11     4 | 14  1  8 16 |     5 10 15
------------+-------------+-------------+------------
   14  7  9 | 15 12       | 11    10  2 |  8    16  6
    2 15  8 | 10 16  1    | 12  4    13 |  9  3 11   
11  1 10 12 |  6    13  9 | 16  8  7 14 |  2  4     5
    6  3 16 | 14  8 11  2 |    15  9  1 | 13       10
------------+-------------+-------------+------------
 2  7 16    | 11  4 14    |  1 10 13  9 | 15  8  3 12
   15  4  1 |    13  7  8 |  3     2  6 | 10  9  5   
 3 13 12 10 | 16 15  9  1 |  4 14  5  8 |  6  2  7 11
 6  9  8    |    10  2    |  7 12 16    | 14 13  1  4
```

You can also generate sudokus of different sizes, using the ``size`` keyword
argument of the ``generate()`` function, which takes a pair
indicating ``(width, height)`` of a region.

```python
from sudokutools.generate import generate

sudoku = generate(size=(2, 5))
print(sudoku)
```

Output:
```
      |  9  8 |  2    |       |     7
      |  2    |     7 |     6 |      
 9  5 |     1 |       |       |      
   10 |       |  9    |     8 |     5
    6 |       |    10 |       |     4
------+-------+-------+-------+------
 8    |  1    |       |    10 |  7   
      |     3 |       |     9 |  4   
    4 |  5    |  7    |       |  3 10
 6    | 10    |       |       |      
      |     2 | 10    |  3    |  9   
```

There's much more that you can do, so be sure to check out the documentation.

## Sudoku in the Shell
+ [Interactive usage](#interactive-usage)
+ [Creating new sudokus](#creating-new-sudokus-1)
+ [Using the stack](#using-the-stack)
+ [Commandline usage](#commandline-usage)

sudokutools comes with a command line shell, which can
be used for basic tasks including creating, printing and solving sudokus.
You can write shell script for this shell as is demonstrated below or
simple use the shell in an interactive mode or read from standard input.
The introduction text and command prompt are only displayed when in
interactive mode. 

The shell operates on an internally saved sudoku (which is empty by default).
Generating a new sudoku or change operations overwrite the current sudoku.
You can however save the current sudoku to a stack (see below). 

### Interactive usage
Typing ```sudokutools``` or ```python -m sudokutools``` will drop you into
the sudokutools shell. Simply type ``help`` for an overview of commands. The
commands provided by the shell behave in the same way as the corresponding
python functions, but the shell also has some unique commands.

```
sudokutools shell 0.2.0
For a list of available command type: help
> generate
> print
    5 | 3     |   7
    6 |       |
  7   | 8 5   | 3
------+-------+------
4     |     2 | 8
3     |   7   | 6   9
      |       | 4
------+-------+------
      |       | 5
5 6 2 |     8 |
  8   |     3 | 9   6
> exit
```

### Creating new sudokus
```
#!/usr/bin/env sudokutools
# Generate 3 sudokus and their solutions and print them.
loop 3
  generate
  encode
  solve
  encode
loop end
```

Output:
```
009070630000056000700200008000507060201000400000090010030000104490300050000000000
529874631843156927716239548984517263251683479367492815635728194498361752172945386
052600700000450001008000000610080002000000010030000400000000020080097003700002106
452619738973458261168723954614985372829374615537261489391546827286197543745832196
008000700500040000670000109203010070000900400000050000080090000300500600040806030
938165742512749863674382159293614578851937426467258391786493215329571684145826937
```

### Using the stack
In the above example sudokus and solutions are mixed in the output. The
sudokutools shell provides a stack on which you can push sudokus in order
to work on multiple sudokus. In this example we first generate and print
3 sudokus while pushing them the stack in order to recall them later to
print their solutions:
```
#!/usr/bin/env sudokutools
# Generate 3 sudokus and their solutions and print them sorted.
loop 3
  generate
  encode
  push
loop end

loop 3
  pop 0
  solve
  encode
loop end
```

Output:
```
009070630000056000700200008000507060201000400000090010030000104490300050000000000
052600700000450001008000000610080002000000010030000400000000020080097003700002106
008000700500040000670000109203010070000900400000050000080090000300500600040806030
529874631843156927716239548984517263251683479367492815635728194498361752172945386
452619738973458261168723954614985372829374615537261489391546827286197543745832196
938165742512749863674382159293614578851937426467258391786493215329571684145826937
```

### Commandline usage
You don't need to write your sudokutools shell scripts into separate files -
the shell can read commands from standard input as well. Even more convenient
is the use of the ``sudokutools -c`` commandline argument. The following
line will do the same job as the first loop example:

```sh
$ sudokutools -c "loop 3; generate; encode; solve; encode; loop end"
```

## Road map and changelog
+ [Version 0.4.0 (planned)](#version-040)
+ [Version 0.3.0 (current)](#version-030)
+ [Version 0.2.0](#version-020)
+ [Version 0.1.1](#version-011)
+ [Version 0.1](#version-01)

### Version 0.4.0
#### Features (planned):
* More solving methods.
* Rating and scoring of sudokus.
* Play mode for the sudokutools shell.


### Version 0.3.0
> This is the current ``sudokutools`` version.

#### Features:
* Added Pointing Pair / Triples and Basic Fishes (X-Wing, Swordfish, Jellyfish)
  to the ``sudokutools.solvers`` module
* Support for arbitrary sudoku sizes

#### Changes:
* Global change: All classes and functions now work with arbitrary sudoku
  sizes.
* Module ``sudokutools.sudoku``:
  * **API change:** ``len(sudoku)`` no longer returns the number of filled
  fields, but the total number of fields, which now depends on the given
  size.
  * **API change:** Coordinate functions ``row_of()``, ``column_of``,
    ``square_of()`` and ``surrounding_of()`` are now methods
    ``Sudoku.row_of()``, ``Sudoku.column_of()``, ``Sudoku.region_of()``
    and ``Sudoku.surrounding_of`` of a ``Sudoku`` instance,
    since they depend on the sudoku size. 
  * Added method: ``Sudoku.__iter__()``, which iterates through
    all (row, column) pairs of a sudoku.
  * Added ``Sudoku.width``, ``Sudoku.height`` and ``Sudoku.height``
    property.
  * Improved method: ``Sudoku.decode()`` is now more versatile.  
* Module ``sudokutools.printing``:
  * **API change:** Module removed. ``view()``
  has been moved to ``sudokutools.sudoku``. 
* Module ``sudokutools.solvers``:
  * **API change:** ``SolveStep.affected`` now only holds field coordindates
    which will actually be changed by applying a step.
  * Added classes ``PointingPair``, ``PointingTriple``, ``XWing``,
    ``Swordfish``, ``Jellyfish``


### Version 0.2.0
#### Features:
* More printing: print the candidates of sudokus
* Different solving strategies, which can be used to learn solving sudokus in
  ``sudokutools.solvers``:
  * Naked singles, naked tuples (pairs, triples, ...)
  * Hidden singles, hidden tuples (pairs, triples, ...)
  * Bruteforce
* Added the sudokutools shell: A commandline interface to sudokutools
* Creating sudokus from pattern templates (like the one at the top of the README)

#### Changes:
* Added module ``sudokutools.printing`` to print sudoku candidates.
* Added module ``sudokutools.shell`` which provides the sudokutools shell.
* Added module ``sudokutools.solvers`` with high-level solving classes.
* Module ``sudokutools.generate``:
  * New function ``generate_from_template()``
* Module ``sudokutools.solve``:
  * **API change:** The ``bruteforce()`` function has been changed.
    The ``reverse`` argument has been removed and it now yields all possible
    solutions.
* Module ``sudokutools.sudoku``:
  * **API change:** The method signature of ``Sudoku.remove_candidates()`` in
  has been changed to be consistent with the signature of
  ``Sudoku.set_candidates()``
  * New method ``Sudoku.set_number()``
* Fixed multiple bugs.


### Version 0.1.1
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
