SMS-Doku
===

A constraints based Soduku solver hooked up to the Twilio SMS api. 

SMS Api
---
Setup a POST /sms as your messaging endoint in the Twilio dashboard. 

Texting 'usage' to your phone number will return some help text. 
Texting
```
solve
....3....
2.......3
..52.86..
...4.1...
.946.753.
..6...8..
.57.2.46.
..3...7..
.825.439.
```

Will return the solved board to you via sms. 

Similarly, 
```
hint
....3....
2.......3
..52.86..
...4.1...
.946.753.
..6...8..
.57.2.46.
..3...7..
.825.439.
```

Will give you one randomly chosen hint from one solution of the board. 

Note that the solver uses just enough brute force to solve the puzzle,
but not enough to determine if there are multiple solutions.

Board Format
***

*  Use [1-9] for known values.
*  Anything non-numeric, 0, periods or spaces work for the unknowns. 
*  Except for spaces in the first cell. 
*  Newlines aren't required, if you're better at typing 81 characters in order

Web API 
--- 
Usable for testing, at this point it just returns the same
text versions as the SMS api.

*  POST the board (in the body as text/plain) to /solve for a solution
*  POST the board to /hint for a single hint


 