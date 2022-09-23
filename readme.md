# Discord Ghost Ball Bot

A bot that will listen on a discord channel, accpeting commands.  
The main commands are `!start`, `!guess [int]` and `!resolve [int]`.

The integer will be between 1 and 1000, and the person with the closest guess will win points.

The point scale is:

* 0-25 - 100 pts
* 26-50 - 75 pts
* 51-75 - 50 pts
* 76-100 - 25 pts

There should also be a running total for each player that can be checked with a command.

## Requirements
