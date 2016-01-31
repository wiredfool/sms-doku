#
# A constraint based Soduku solver.  Written in anger 1/28/2011 in a
# contest to see if I could write this faster than solving the puzzle
# directly. turns out that this took about twice as long as doing one
# puzzle.
# 
# Eric Soroos 2011-2014
# 
# undone - tests in test.py 

import itertools

cardinality = 3
card_sq = 9


def dbg(s): 
    pass
    #print(s)

    
class cell(object):
    
    def __init__(self,v):
        try:
            v = int(v)
            self.val=v
        except:
            self.val = 0
        self.constraints = []
        self.row = None
        self.col = None
        self.square = None
        
    def pprint(self):
        if self.val:
            return str(self.val)
        return '.'

    def add_constraint(self, con):
        if self.val: return
        if not con in self.constraints:
            self.constraints.append(con)

    def dof(self):
        if self.val: return 0
        return card_sq - len(self.constraints)

    def is_possible(self,v):
        if self.val: return v == self.val
        return v not in self.constraints

    def get_possible(self):
        return [i for i in range(1,card_sq+1) if self.is_possible(i)]
    
    def solve(self):
        if self.val: return False
        if self.dof() > 1: return False
        self.constraints.sort()
        i=1
        for j in self.constraints:
            if j != i:
                break
            i+=1
        # if we fall through, then 9, if not, then 1..8
        if i <= card_sq:
            self.val=i
            dbg( "Found cell: row %s col %s val %s" % (self.row, self.col, self.val))
            return self.val
        return False

    def dump(self):
        return "\n".join(["%s=%s"%(att, getattr(self,att))
                          for att in ['val', 'constraints', 'row', 'col', 'square']])


class board(object):

    def __init__(self, initial):
        self.rows = []
        if '\n' in initial:
            # assume \n is a better marker of EOL than trailing whitespace
            initial = initial.replace('\r', '')
            lines = initial.split('\n')
            initial = "".join("%-9s" % l for l in lines)

        while initial:
            line = initial[:9]
            initial = initial[9:]
            row=[]
            for ch in line:
                row.append(cell(ch))
            for i in range(len(row),card_sq):
                row.append(cell(0))
            #print len(row)
            self.rows.append(row)
        self.success = range(1,card_sq+1)
        self.cols = []
        self.squares = []
        self.open = []
        self.next = []
        self.found = set()
        self.fill_alts()

    def fill_alts(self):
        # need to invert rows to cols
        for i in self.success:
            self.cols.append([])
            self.squares.append([])
            
        for row in self.rows:
            i=0;
            for c in row:
                self.cols[i].append(c)
                i+=1

        i=0
        for row in self.rows:
            j=0
            for c in row:
                c.row = i
                c.col = j
                c.square = (i/3)*cardinality+(j/3)
                self.squares[c.square].append(c)
                j+=1
            i+=1

        for row in self.rows:
            for c in row:
                if c.val:
                    self.add_constraint(c)
                else:
                    self.open.append(c)
                
        #self.pprint(self.rows)
        #self.pprint(self.cols)
        #self.pprint(self.squares)


    def pprint_row(self, row):
        return "%s  %s  %s" %(row[:3], row[3:6], row[6:])

    def pprint(self, arr):
        for i,row in enumerate(arr):
            dbg( "%s   %s" %(self.pprint_row("".join([c.pprint() for c in row])),
                             self.pprint_row("".join([str(c.dof()) for c in row]))))
            if (i+1)%3 == 0:
                dbg('')
        dbg('')


    def dump(self):
        return "\n".join(["".join([str(r.val) for r in row]) for row in self.rows])
        
    def check_arr(self,arr, name):
        r = [c.val for c in arr]
        if 0 in r:
            dbg( "None Found")
            return False
        r.sort()
        if r != self.success:
            dbg( "%s Invalid" %name)
            return False
        return True
    
    def solved(self):
        #check rows

        for row in self.rows:
            if not self.check_arr(row, 'row'):
                return False

        for col in self.cols:
            if not self.check_arr(col, 'col'):
                return False

        for square in self.squares:
            if not self.check_arr(square, 'square'):
                return False

        return True

    def add_constraint(self, cell):
        if not cell.val:
            return False
        for c in itertools.chain(self.rows[cell.row],
                                 self.cols[cell.col],
                                 self.squares[cell.square]):
            c.add_constraint(cell.val)
            if c.dof() == 1:
                if c not in self.next:
                    self.next.append(c)

    def _step(self):
        if len(self.next):
            c = self.next.pop()
            if c.solve():
                self.add_constraint(c)
                self.found.add(c)
                self.open.remove(c)
                return len(self.open)
            else:
                dbg( "Dof=1, didn't solve, from next")
                dbg( c.dump())
                return False

        # next strategy, now that we've ruled out all of the one dof ones
        # look through each cluster for cases where there's only cell that can
        # have a value, though it may have others that haven't been ruled out yet. 

        for cell in self.open:
            poss = cell.get_possible()
            #print "Checking cell %s %s, possible: %s" % (cell.row, cell.col, poss)
            for val in poss:
                #check the row, col, and square. If anyone of these is the only one
                # not ruled out, then we apply it, and apply the new constraints,
                # and then iterated. 
                for arr in [self.rows[cell.row],
                            self.cols[cell.col],
                            self.squares[cell.square]]:
                    found = False
                    for c in arr:
                        if c!= cell and c.is_possible(val):
                            found=True
                            #print " Ruled out %s at %s %s" % (val, c.row, c.col)
                            break
                    if not found:
                        cell.val = val
                        self.add_constraint(cell) 
                        self.open.remove(cell)
                        self.found.add(cell)
                        dbg( "Found cell by possiblity: row %s col %s val %s" % (cell.row, cell.col, cell.val))
                        return True

    def find_min_dof(self):
        min_dof = card_sq
        min_loc = 0
        i = 0
        for c in self.open:
            dof = c.dof()
            if dof < min_dof:
                min_dof=dof
                min_loc = i
            i+=1
        #dbg( "Min DOF left: %s" %(min_dof))
        #dbg( self.open[min_loc].dump())
            
        return self.open[min_loc]

    def solve(self, rlevel=10):
        self.pprint(self.rows)
        cont = True
        while cont:
            cont = self._step()
            self.pprint(self.rows)
            dbg( "%s more ready to solve" % len(self.next))

        if len(self.open) and rlevel:
            dbg( "All simple deterministic strategies spent, trying speculative")

            min_dof_cell = self.find_min_dof()
            dbg( min_dof_cell.dump())
            poss = min_dof_cell.get_possible()
            str_board = self.dump()
            spec_boards = [board(str_board) for p in poss]
            for (b,val) in zip(spec_boards, poss):
                cell = b.rows[min_dof_cell.row][min_dof_cell.col]
                cell.val = val
                b.add_constraint(cell)
                b.open.remove(cell)
                b.found.add(cell)
                dbg( "Solving Spec: possiblility %s, rlevel %s, pos: %s,%s" % (val,
                                                                                rlevel,
                                                                                cell.row,
                                                                                cell.col))
                if b.solve(rlevel-1):
                    dbg( "Solved using speculation")
                    self.rows = b.rows
                    self.found.update(b.found)
                    return True
            
        dbg("Is Solved? %s" % self.solved())
        return self.solved()

    def hint(self):
        if self.solve():
            return self.found.pop()
        return None
        
test1="""123456789
456789123
789123456
234567891
567891234
891234567
345678912
678912345
912345678"""

#b = board(test1)
#print b.solved()

test2="""123456780
456789120
789123450
234567890
567891230
891234560
345678910
678912340
912345670"""

#b = board(test2)
#b.solve()

# requires secondary strategey, setting one when its
# ruled out for all the other members of row,col,or square.
book_test1="""1
 8 5   3
 3 42
 937
  861 9
5   8362
75  68
  9  578
  63    1"""

# easy, directly solves it.
book_test9="""    3
2       3
  52 86
   4 1
 946 753
  6   8
 57 2 46
  3   7
 825 439"""

#level 2
book_test11="""
    15  9
   3  176
  8 24  3
 2 6    5
 9 1  7
  6  2 5
  3   28
 1289"""

#level 3 - needs recursive algo, 1 deep, or possibly something deterministic, but smarter.
book_test71="""      2
   5   1
547
8 67 2  4
  2  598
3 54 9  6
238
   3   6
      7"""

# level 3 needs 2 speculative guesses, 
book_test99="""   3
   6  71
 35 2 4
68 9  3
        2
97 8  5
 49 8 1
   5  93
   1"""


dots = """....3....
2.......3
..52.86..
...4.1...
.946.753.
..6...8..
.57.2.46.
..3...7..
.825.439."""

# world's hardest soduku - kristanix.com, requires 8 levels of speculation, 1 sec, netbook
hardest="""1    7 9
 3  2   8
  96  5
  53  9
 1  8   2
6    4
3      1
 4      7
  7   3"""

# world's hardest, according to the guardian, solved @ 6 levels, 1 sec, netbook
hardest2="""  53
8      2
 7  1 5
4    53
 1  7   6
  32   8
 6 5    9
  4    3
     97"""

if __name__=='__main__':
    b = board(dots)
#b.pprint(b.squares)
    b.solve(10)
    print b.dump()
    print len(b.found)
    cell = b.found.pop()
    print "%d, %d, %d" %(cell.val, cell.row+1, cell.col+1)
