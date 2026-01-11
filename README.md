# Usage

Run `server.py` on the host computer:
```bash
./server.py
```

Run `main.py` on two client computer
```bash
./main.py
```
Then enter the ip of the host computer, displayed in the server terminal.

### Rules

The **goal** of the game is to be the first to get all of your the pieces to the finish. Each piece starts from the middle and also arrives there, doing a loop.  

Every round starts by **rolling** the four 'dice'. The amount of white corners pointing up determines your moves. You are most likely to roll a 2 and it is also possible to roll a 0. In this case you skip your turn.  

The middle column of the board is shared between the two players. Here the enemy can be **captured** by moving _to the same tile_. Captured piece return to the hands of the player. You cannot capture your own pieces but you can jump over any pieces. There is a possibility that you have no valid moves. In this case you skip your turn.  

There are **rosettes** on the board. _Stopping_ on them grants an extra turn. Pieces on them cannot be captured.

### Requirements:
- python
- pygame
