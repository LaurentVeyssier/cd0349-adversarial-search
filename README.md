
# Project: Build an Adversarial Game Playing Agent

![Example game of isolation on a square board](viz.gif)

## Synopsis

In this project, you will experiment with adversarial search techniques by building an agent to play knights Isolation.  Unlike the examples in lecture where the players control tokens that move like chess queens, this version of Isolation gives each agent control over a single token that moves in L-shaped movements--like a knight in chess.

### Isolation

In the game Isolation, two players each control their own single token and alternate taking turns moving the token from one cell to another on a rectangular grid.  Whenever a token occupies a cell, that cell becomes blocked for the remainder of the game.  An open cell available for a token to move into is called a "liberty".  The first player with no remaining liberties for their token loses the game, and their opponent is declared the winner.

In knights Isolation, tokens can move to any open cell that is 2-rows and 1-column or 2-columns and 1-row away from their current position on the board.  On a blank board, this means that tokens have at most eight liberties surrounding their current location.  Token movement is blocked at the edges of the board (the board does not wrap around the edges), however, tokens can "jump" blocked or occupied spaces (just like a knight in chess).

Finally, agents have a fixed time limit (150 milliseconds by default) to search for the best move and respond.  The search will be automatically cut off after the time limit expires, and the active agent will forfeit the game if it has not chosen a move.

**You can find more information (including implementation details) about the in the Isolation library readme [here](/isolation/README.md).**


## Getting Started (Workspaces)


#### The get_action() Method
This function is called once per turn for each player. The calling function handles the time limit and 
```
def get_action(self, state):
    import random
    self.queue.put(random.choice(state.actions()))
```



#### Initialization Data
Your agent will automatically read the contents of a file named `data.pickle` if it exists in the same folder as `my_custom_player.py`. The serialized object from the pickle file will be assigned to `self.data`. Your agent should not write to or modify the contents of the pickle file during search.

The log file will record a warning message if there is no data file, however a data file is NOT required unless you need it for your opening book. (You are allowed to use the data file to provide _any_ initialization information to your agent; it is not limited to an opening book.)




### Option 2: Develop an opening book (must span at least depth 4 of the search tree)

- Write your own code to develop an opening book of the best moves for every possible game state from an empty board to at least a depth of 4 plies
- Create a performance baseline using `run_search.py` (with the `fair_matches` flag _disabled_) to evaluate the effectiveness of your agent using randomly chosen opening moves.  (You can use any heuristic function, but you should use the same heuristic on your agent for all experiments.)
- Use the same procedure to evaluate the effectiveness of your agent when early moves are selected from your opening book

**Hints:**
- Developing an opening book can require long run-times to simulate games and accumulate outcome statistics
- If the results are very close, try increasing the number of matches (e.g., >100) to increase your confidence in the results

