
from sample_players import DataPlayer
from isolation import Isolation,DebugState
import pickle, os

class CustomPlayer(DataPlayer):
    """ Implement your own agent to play knight's Isolation

    The get_action() method is the only required method for this project.
    You can modify the interface for get_action by adding named parameters
    with default values, but the function MUST remain compatible with the
    default interface.

    **********************************************************************
    NOTES:
    - The test cases will NOT be run on a machine with GPU access, nor be
      suitable for using any other machine learning techniques.

    - You can pass state forward to your agent on the next turn by assigning
      any pickleable object to the self.context attribute.
    **********************************************************************
    """
    def get_action(self, state):
        """ Employ an adversarial search technique to choose an action
        available in the current state calls self.queue.put(ACTION) at least

        This method must call self.queue.put(ACTION) at least once, and may
        call it as many times as you want; the caller will be responsible
        for cutting off the function after the search time limit has expired.

        See RandomPlayer and GreedyPlayer in sample_players for more examples.

        **********************************************************************
        NOTE: 
        - The caller is responsible for cutting off search, so calling
          get_action() from your own code will create an infinite loop!
          Refer to (and use!) the Isolation.play() function to run games.
        **********************************************************************
        """
        # TODO: Replace the example implementation below with your own search
        #       method by combining techniques from lecture
        #
        # EXAMPLE: choose a random move without any search--this function MUST
        #          call self.queue.put(ACTION) at least once before time expires
        #          (the timer is automatically managed for you)
        #import random
        #self.queue.put(random.choice(state.actions()))

        # check if book of openings exists, else create one
        #if state.context is None:
        if not os.path.exists("data.pickle"):
                print('Book of openings not found, creating one...')
                player1 = CustomPlayer(0)
                player1.build_book( num_simulations=10,
                                    NUM_ROUNDS=5_000,
                                    depth_limit=100)
                
        with open("data.pickle", 'rb') as f:
          self.data = pickle.load(f)

        # if book of openings exists, play the best opening move
        if state.board in self.data:
            self.queue.put(self.data[state.board])
            print("Playing best opening move...")
        else:
            a = self.alpha_beta_search(state, depth=4)
            self.queue.put(a)
            print(f"{state.player()} playing {a}")
            print(DebugState.from_state(state.result(a)))







    def my_moves(self, gameState):
        return len(gameState.liberties(gameState.locs[0])) - len(gameState.liberties(gameState.locs[1]))


    def alpha_beta_search(self, gameState, depth):
        """ Return the move along a branch of the game tree that
        has the best possible value.  A move is a pair of coordinates
        in (column, row) order corresponding to a legal move for
        the searching player.
        
        You can ignore the special case of calling this function
        from a terminal state.
        """
        alpha = float("-inf")
        beta = float("inf")
        best_score = float("-inf")
        best_move = None
        for a in gameState.actions():
            v = self.min_value(gameState.result(a), alpha, beta, depth - 1)
            alpha = max(alpha, v)
            if v > best_score:
                best_score = v
                best_move = a
        return best_move

    def min_value(self, gameState, alpha, beta, depth):
        """ Return the value for a win (+1) if the game is over,
        otherwise return the minimum value over all legal child
        nodes.
        """
        if gameState.terminal_test():
            return gameState.utility(0)
        
        if depth <= 0:
            return self.my_moves(gameState)
        
        v = float("inf")
        for a in gameState.actions():
            v = min(v, self.max_value(gameState.result(a), alpha, beta, depth - 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def max_value(self, gameState, alpha, beta, depth):
        """ Return the value for a loss (-1) if the game is over,
        otherwise return the maximum value over all legal child
        nodes.
        """
        if gameState.terminal_test():
            return gameState.utility(0)
        
        if depth <= 0:
            return self.my_moves(gameState)
        
        v = float("-inf")
        for a in gameState.actions():
            v = max(v, self.min_value(gameState.result(a), alpha, beta, depth -1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    '''def get_action(self, gameState, depth_limit):
        for depth in range(1, depth_limit + 1):
            action = self.alpha_beta_search(gameState, depth)
            print("Depth: {} -> Action: {}".format(depth, action))'''



    def build_book(self, num_simulations, NUM_ROUNDS, depth_limit):
        """ Build a book of moves from the current state to the given depth
        """
        import random, pickle
        import pandas as pd
        from tqdm import tqdm
        #import matplotlib.pyplot as plt

        def build_table(num_rounds=NUM_ROUNDS, depth=depth_limit):
            # Builds a table that maps from game state -> action
            # by choosing the action that accumulates the most
            # wins for the active player. (Note that this uses
            # raw win counts, which are a poor statistic to
            # estimate the value of an action; better statistics
            # exist.)
            from collections import defaultdict, Counter
            book = defaultdict(Counter)
            for _ in range(num_rounds):
                state = Isolation()
                build_tree(state, book, depth)
            return {k: max(v, key=v.get) for k, v in book.items()}


        def build_tree(state, book, depth):
            if depth <= 0 or state.terminal_test():
                return -simulate(state)
            action = random.choice(state.actions())
            reward = build_tree(state.result(action), book, depth - 1)
            book[state][action] += reward
            return -reward


        def simulate(state):
            player_id = state.player()
            while not state.terminal_test():
                state = state.result(random.choice(state.actions()))
            return -1 if state.utility(player_id) < 0 else 1
    
        # board array dimensions and bitboard size
        _WIDTH = 11
        _HEIGHT = 9
        _SIZE = (_WIDTH + 2) * _HEIGHT - 2
        opening_book = pd.DataFrame()

        # Do n simulations to collect winning opening moves with rate > 60%
        book_best_openings = {}
        for _ in tqdm(range(num_simulations)):
          # build a book of openings
          book = build_table(NUM_ROUNDS, depth_limit)
          # initialize a dataframe to store the win/loss count for each opening move
          pd.set_option('future.no_silent_downcasting', True)
          win_moves_df = pd.DataFrame(columns=['win', 'loss'], index=range(0,_SIZE)).fillna(0)
          # collect win/loss statistics per opening in the book
          for i, b in enumerate(tqdm(list(book), leave=False)):
              # check if this move leads to a terminal state
              new_b = b.result(book[b])
              if new_b.terminal_test():
                  #dbstate = DebugState.from_state(new_b)
                  #print(dbstate)
                  # find initial move and winner player
                  num_moves = b.ply_count
                  winner = [0 if new_b.utility(0)>0 else 1][0]
                  try:
                      # filter the first move corresponding to this winning sequence
                      initial_state = list(book)[i + num_moves - 1]
                      initial_move = initial_state.locs[0]
                      # log statistics in dataframe
                      if winner == 0:
                          win_moves_df.loc[initial_move,'win']+=1
                      else:
                          win_moves_df.loc[initial_move,'loss']+=1
                  except:
                      pass
              
          # remove opening moves that have not been tested in this book
          win_moves_df.drop(win_moves_df.loc[(win_moves_df['win']== 0) & (win_moves_df['loss']== 0)].index, inplace=True)
          # calculate the net win/loss and % win for each opening move
          win_moves_df['net'] = win_moves_df['win'] - win_moves_df['loss']
          win_moves_df['loss'] = win_moves_df['loss'] * -1
          win_moves_df['% win'] = (win_moves_df['win'] / (win_moves_df['win'] - win_moves_df['loss']) * 100).round(1)
          # sort the opening moves by net win/loss
          sorted_win_moves_df = win_moves_df.sort_values('net', ascending=False)

          '''
          # to display the book openings by winning rate
          fig, ax = plt.subplots(figsize=(30,5))
          sorted_win_moves_df[['win','loss']].plot(kind='bar',stacked=True, ax=ax)
          ax.scatter(sorted_win_moves_df.index.astype(str), sorted_win_moves_df['net'],  color=[1,0,0], label='net')
          ax.legend()
          plt.title("Best openings for player 1 (win - loss and Net)")
          plt.show()'''

          # keep only the opening moves with winning rate > 60%
          opening_book = pd.concat([opening_book,sorted_win_moves_df[sorted_win_moves_df['% win']>60]])
          opening_book = opening_book.reset_index().groupby('index').sum()
          opening_book['% win'] = (opening_book['win'] / (opening_book['win'] - opening_book['loss']) * 100).round(1)

          
          # Now that we have collected only best openings, 
          # accumulate the winning opening moves into book_best_openings
          # go through all step in the book sample
          all_states, all_moves = list(book.keys()), list(book.values()) 
          winning_openings = {}
          for i, b in enumerate(tqdm(book)):
              # select only winning moves for player 0
              new_b = b.result(book[b])
              if new_b.terminal_test():
                  if new_b.utility(0)>0:
                      # find the total number of moves in this winning sequence
                      num_moves = b.ply_count
                      try:
                          # we grab the full sequence of moves that led to this winning state
                          initial_state = all_states[i + num_moves - 1]
                          initial_move = initial_state.locs[0]
                          # we keep the sequence only if the opening belongs to the best above 60% winning rate
                          if initial_move in opening_book.index:
                              winning_openings = {s.board:m for s,m in zip(all_states[i: i + num_moves],all_moves[i: i + num_moves])}
                              book_best_openings.update(winning_openings)
                      except:
                          pass
                          
        # SAVE BOOK OF ALL BEST WINNING SEQUENCES TO PICKLE FILE
        with open("data.pickle", 'wb') as f:
            pickle.dump(book_best_openings, f)



'''if __name__ == "__main__":
    player1 = CustomPlayer(0)
    player1.build_book(num_simulations=10,
                       NUM_ROUNDS=5_000,
                       depth_limit=100)'''

