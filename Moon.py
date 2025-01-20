class GameAlreadyWon(Exception):
    pass

class Moon():
    def __init__(self, initial = [[0]*7, [0]*7], gone_to_phase_2 = False, nb_w = 6, nb_b =6, player=1):
        # a state is [outside_array, inside_array]
        # +1 for white, -1 for black, 0 for empty
        self.gone_to_phase_2 = gone_to_phase_2
        self.state = initial.copy()
        self.player = player
        self.nb_b = nb_b
        self.nb_w = nb_w
        self.winner = None
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.state == other.state)*(self.player == other.player)
        else:
            return False

    def __hash__(self):
        return hash((self.state[0][0], self.state[0][1], self.state[0][2], self.state[0][3], self.state[0][4], self.state[0][5], self.state[0][6],\
                     self.state[1][0],self.state[1][1], self.state[1][2], self.state[1][3], self.state[1][4], self.state[1][5], self.state[1][6],\
                     self.player))

    def phase(self):
        if self.gone_to_phase_2:
            return 2
        else:
            if self.nb_b == self.nb_w or self.nb_b == self.nb_w + 1:
                return 1
            else:
                return 2

    def get_rmn(self):
        return (self.player==1)*self.nb_w + (self.player==-1)*self.nb_b
    def set_rmn(self):
        raise Exception("Don't set the rmn.") 
    
    def get_other_rmn(self):
        return (self.player==1)*self.nb_b + (self.player==-1)*self.nb_w
    def set_other_rmn(self):
        raise Exception("Don't set the other rmn.")
    
    # a call to rmn and (other_rmn) give the amount of remaining tokens of the current player 
    rmn = property(get_rmn, set_rmn)
    # (and of the other one) 
    other_rmn = property(get_other_rmn, set_other_rmn)

    # synthesizes the game
    def __repr__(self) -> str:
        rep = f"EXT: {self.state[0]} INT: {self.state[1]} - "
        rep += f"W: {self.nb_w} - B: {self.nb_b} - "
        rep += f"Rmn: {self.get_rmn()} - "

        if self.winner !=None:
            rep += f"Winner: {self.winner}."
        else:
            rep += f"Player: {self.player}."
        return rep
    
    @classmethod
    def other_player(cls, player):
        return -player

    def switch_player(self):
        self.player = Moon.other_player(self.player)

    def next_phase(self):
        if self.phase == 2:
            pass
        else:
            if self.nb_b == 0 and self.nb_w == 0:
                self.gone_to_phase_2 = True

    def is_won(self):
        outside = self.state[0]
        inside = self.state[1]
        for i in range(7):
            for player in [self.player, self.other_player]:    
                for side in [outside, inside]:
                    if player == side[i] :
                        if side[(i+1)%7] == side[i] and side[(i+2)%7] == side[i] and side[(i+3)%7] == side[i]:
                            return True
                if player == outside[i] :
                    if inside[(i+1)%7]  == outside[i] and inside[(i+3)%7]  == outside[i] and outside[(i+4)%7]  == outside[i]:
                        return True
        return False
    
    def p1_available_actions(self):
        """Computes the actions that are valid in phase 1.
            Returns a set of tuples (in/out, index)"""
        if self.is_won():
            return None
        actions = set()
        for i in range(2):
            for j in range(7):
                if self.state[i][j] == 0:
                    actions.add((i, j))
        return actions

    def p2_available_actions(self):
        """
            Computes the actions that are valid in phase 2.
            Returns a set of tuples (FROM :(in/out, index), TO :(in/out, index), 
                                     CAPTURE :(in/out, index) (-1,-1) if no capture, 
                                     CHOICE : None, F (capture a friend), NF (no capture), 
                                              C (capturing an enemy while it could also move 
                                              without doing so because it's a direct neighbor)))
        """
        
        actions = set()
        for i in range(2):
            for j in range(7):
                # put a chip on an empty space
                if self.state[i][j] == 0:
                    if self.player == 1 and self.nb_w > 0:
                        actions.add(((-1,-1),(i,j),(-1,-1),None))
                    if self.player == -1 and self.nb_b > 0:
                        actions.add(((-1,-1),(i,j),(-1,-1),None))
                if self.state[i][j]==self.player:
                    for ((m,n),second) in neighbors((i,j)):
                        # empty neighbors
                        if self.state[m][n]==0:
                            actions.add(((i,j),(m,n),(-1,-1),None))
                        # jumping over an ennemy or a friend
                        else:
                            if second:
                                (k,l) = second
                                if self.state[k][l]==0:
                                    if self.state[m][n]==self.player:
                                        actions.add(((i,j),(k,l),(m,n),"F"))
                                        actions.add(((i,j),(k,l),(-1,-1),"NF"))
                                    else:
                                        if (k,l) in {n[1] for n in neighbors((i,j))}:
                                            actions.add(((i,j),(k,l),(m,n),"C"))
                                        else:
                                            actions.add(((i,j),(k,l),(m,n),None))
        return actions
    
    def play_random(self):
        from random import choice as choose
        if self.phase() == 1:
            action = choose(list(self.p1_available_actions()))
            self.play(action, 1)
                 
        else :
            action = choose(list(self.p2_available_actions()))
            self.play(action,2)
        self.next_phase() 

    def play(self, action, phase):
        if self.winner :
            pass
        if phase == 1:
            (i,j) = action
            rmn = (self.player == -1)*self.nb_b + (self.player == 1)*self.nb_w
            if rmn == 0:
                raise Exception(ValueError, "Invalid action.")
            self.state[i][j] = self.player
            self.nb_b -= (self.player == -1)
            self.nb_w -= (self.player == 1)
      
        if phase == 2:
            (wherefrom, whereto, capt, ch) = action
            (i,j) = wherefrom
            (k,l) = whereto
            rmn = (self.player == -1)*self.nb_b + (self.player == 1)*self.nb_w
            if wherefrom[0] == -1:
                if rmn > 0:
                    self.state[k][l] = self.player
                    self.nb_b -= (self.player == -1)
                    self.nb_w -= (self.player == 1)
                else:
                    raise Exception(ValueError, "Can't play this action - not enough chips !")

            else:
                self.state[i][j] = 0
                self.state[k][l] = self.player
                if capt[0] == -1:
                    pass
                else:
                    (m,n) = capt
                    if ch == "F":
                        self.state[m][n] = 0
                        if self.player == 1:
                            self.nb_w +=1
                        else:
                            self.nb_b +=1
                    elif ch == "NF":
                        pass
                    else:
                        self.state[m][n] = 0
                        if self.player == 1:
                            self.nb_b +=1
                        else:
                            self.nb_w +=1
        
        if self.is_won():
            self.winner = self.player
        
        self.switch_player()
        
# list of all pairs of neighbors, first and second if it exists ((i,j),(i+,j+))
def neighbors(tuple):
    neigh = []
    i = tuple[1]
    if tuple[0]==0:
        neigh.append(((0,(i+1)%7),(0,(i+2)%7)))
        neigh.append(((0,(i+6)%7),(0,(i+5)%7)))
        neigh.append(((1,(i+3)%7),(1,(i+1)%7)))
        neigh.append(((1,(i+4)%7),(1,(i+6)%7)))
    if tuple[0]==1:
        neigh.append(((1,(i+1)%7),(1,(i+2)%7)))
        neigh.append(((1,(i+6)%7),(1,(i+5)%7)))
        neigh.append(((1,(i+2)%7),(0,(i+6)%7)))
        neigh.append(((1,(i+5)%7),(0,(i+1)%7)))
        neigh.append(((0,(i+3)%7),None))
        neigh.append(((0,(i+4)%7),None))
    return neigh
