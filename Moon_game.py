from Moon import Moon
import pygame
from pygame.locals import *
import os

counters_positions = [(86,26),(445,26)]
token_positions = [[(270,88),(411,157),(446,310),(348,433),(190,433),(92,311),(127,156)],
                    [(268,346),(209,317),(194,253),(236,202),(301,202),(342,253),(329,315)]]

def load_png(name):
    """ Load image and return image object"""
    fullname = os.path.join("contents", name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except FileNotFoundError:
        print(f"Cannot load image: {fullname}")
        raise SystemExit
    return image, image.get_rect()
    
def clickable_from_game(game):
    """ Compute from the state of the game the set of clickable positions, i.e. tuples :
        (screen_coordinates : tuple (posx,posy), 
        direct : boolean, 
        Moon_coordinates : tuple (row, index))
    """
    if not isinstance(game, Moon):
        raise TypeError("game must be a Moon instance")
    else:
        clickable = set()
        # phase 1 > all the clickable are on the empty cases
        # computed from (p1_available_actions)
        if game.phase() == 1 and game.nb_b != 0:
            for action in game.p1_available_actions():
                row = action[0]
                index = action[1]
                position = token_positions[row][index]
                if game.player == 1 and game.nb_w > 0:
                    clickable.add((position, True, action))
                if game.player == -1 and game.nb_b > 0:
                    clickable.add((position, True, action))
        # phase 2 > clickable for direct actions (empty cases)
        # and indirect actions (case to move a token from)
        else:
            for action in game.p2_available_actions():
                # direct actions
                if action[0][0] == -1:
                    row = action[1][0]
                    index = action[1][1]
                    position = token_positions[row][index]
                    if game.player == 1 and game.nb_w > 0:
                        clickable.add((position, True, action[1]))
                    if game.player == -1 and game.nb_b > 0:
                        clickable.add((position, True, action[1]))
                # indirect actions : position of the token to move
                else:
                    row = action[0][0]
                    index = action[0][1]
                    position = token_positions[row][index]
                    clickable.add((position, False, action[0]))
        return clickable

def actions_from_source(source_of_alternatives, game):
    """ 
        We're in phase 2. A source (token to move) has been chosen.
        The function computes all possible  to be played from the source.
        Returns a set of tuples :
            (screen_coordinates : tuple (posx,posy), 
             ambiguous : boolean, 
             Moon_coordinates : tuple (row, index),
             alternatives : Moon_action (tuple) or tuple of 2 tuples (Moon_action, description)
            )
    """
    if not isinstance(game,Moon):
        raise TypeError("game should be a Moon instance")
    
    dict_of_alternatives = dict()
    possible_actions = set()

    actions = game.p2_available_actions()
    # select only the actions that have the token position for origin
    actions_set = set(action for action in actions if action[0] == source_of_alternatives)
    # list all possible destinations
    possible_destinations = [action[1] for action in actions_set]
    for destination in possible_destinations:
        # list all actions that allow to go from the origin to this specific destination
        trajectories = set(action for action in actions_set if action[1] == destination)
        # simple case : only one way
        if len(trajectories) == 1:
            action = trajectories.pop()
            action_row = destination[0]
            action_index = destination[1]
            action_coordinates = token_positions[action_row][action_index]
            possible_actions.add((action_coordinates, False, destination, action))
        # ambiguous case : two alternatives
        else:  
            # C marker: choose between jump over the ennemy or direct way
            C_marker = set(traject for traject in trajectories if traject[3]=="C")
            # F marker : choose between take back own token or not
            F_marker = set(traject for traject in trajectories if traject[3]=="F")
            if C_marker:
                act = C_marker.pop()
                dict_of_alternatives[destination] = ((act, "Take that back !"),
                                                     ((act[0],act[1],(-1,-1),None), "I come in peace."))
            if F_marker:
                act = F_marker.pop()
                dict_of_alternatives[destination] = ((act, "I want it back !"),
                                                     ((act[0],act[1],(-1,-1),"NF"), "Leave it here..."))
            action_row = destination[0]
            action_index = destination[1]
            action_coordinates = token_positions[action_row][action_index]
            possible_actions.add((action_coordinates, True, destination, dict_of_alternatives[destination]))

    return possible_actions


def main():
    # size in pixel (square screen)
    screen_size = 540
    running = True
    Game = Moon([[0]*7,[0]*7],gone_to_phase_2=False,nb_w=6,nb_b=6,player=1)
    
    # Variable loop: 1 Welcome_loop, 2 Game_loop, 3 Game_over, 4 Choice, 5 Choice_suppl
    loop = 1
    # where_to_click : set of tuples (screen_coordinates tuple (,), direct or not Boolean)
    where_to_click = set()
    # source_of_alternatives : Moon position of the origin to compute alternatives from 
    source_of_alternatives = None
    # alternatives : list of 2 tuples (Moon_action, description) that inform about
    # the alternatives for the action which choice is being waited for
    alternatives = []

    board_to_do = True
    selection_to_do = True
    
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((screen_size,screen_size), pygame.SRCALPHA)
    pygame.display.set_caption('Moon')
    pygame.event.set_allowed([pygame.QUIT,pygame.MOUSEBUTTONUP])
    
    # load esthetics
    accueil, accueil_rect = load_png("welcome_Moon.png")
    plateau, _ = load_png("board.png")
    play_libre, play_libre_rect = load_png("welcome_button_free.png")
    play_encl, _ = load_png("welcome_button_clicked.png")
    random_enclenche, random_enclenche_rect = load_png("random_bouton_clicked.png")
    random_enclenche_rect.centerx = 473
    random_enclenche_rect.centery = 489
    select, selrect = load_png("selection.png")
    white, _ = load_png("token_white.png")
    black, _ = load_png("token_black.png")
    selected, selectedrect = load_png("token_selected.png")
    
    while running:
        # welcome loop
        if loop == 1:
            # Render the welcome screen
            play_libre_rect.centerx = accueil_rect.centerx
            play_libre_rect.centery = accueil_rect.centery+200
            accueil.blit(play_libre, play_libre_rect)
            screen.blit(accueil, (0, 0))
            pygame.display.update()

            # Listen for collisions
            if play_libre_rect.collidepoint(pygame.mouse.get_pos()):
                accueil.blit(play_encl, play_libre_rect)

            for event in pygame.event.get():
                # If Event QUIT, quit
                if event.type == pygame.QUIT:
                    running = False
                # If Play button, go to game phase
                if event.type == pygame.MOUSEBUTTONUP:
                    if play_libre_rect.collidepoint(pygame.mouse.get_pos()):
                        loop = 2

        # play loop    
        if loop == 2 :
            screen.fill((0,0,0))
            where_to_click = clickable_from_game(Game)

            # Render the game screen : played tokens, nb of remaining tokens, current player
            font1 = pygame.font.Font(None, 55)
            font2 = pygame.font.Font(None, 45)
            font4 = pygame.font.Font(None, 35)
            b_count = font1.render(f'{Game.nb_b}', True, (100,255,0), None)
            w_count = font1.render(f'{Game.nb_w}', True, (100,255,0), None)
            phase = font4.render(f'Phase {Game.phase()}', True, (30,170,0), None)
            plateau.blit(b_count,counters_positions[0])
            plateau.blit(w_count,counters_positions[1])
            plateau.blit(phase,(accueil_rect.centerx - 40, accueil_rect.centery - 255))
            if Game.player == 1:
                player = font2.render("White playing", True, (30,170,0), None)
            else : 
                player = font2.render("Black playing", True, (30,170,0), None)
            plateau.blit(player, (20,495))
            screen.blit(plateau,(0,0))
            pygame.time.wait(15)
            pygame.display.update()
            
            if board_to_do:
                # Display the board
                [outrow,inrow] = Game.state
                for i, case in enumerate(outrow):
                    if case == 1:
                        plateau.blit(white, (token_positions[0][i][0]-18, token_positions[0][i][1]-18))    
                    elif case == -1 :
                        plateau.blit(black, (token_positions[0][i][0]-18, token_positions[0][i][1]-18))
                for i, case in enumerate(inrow):
                    if case == 1:
                        plateau.blit(white, (token_positions[1][i][0]-18, token_positions[1][i][1]-18))    
                    elif case == -1 :
                        plateau.blit(black, (token_positions[1][i][0]-18, token_positions[1][i][1]-18))
                pygame.display.update()
                board_to_do = False
            
            # if the game is won, quit
            if Game.winner:
                loop = 3
            
            else:
               # Listen for collisions:
                for clickable in where_to_click:
                    clickable_pos = clickable[0]
                    selrect.centerx = clickable_pos[0]
                    selrect.centery = clickable_pos[1]
                    if selrect.collidepoint(pygame.mouse.get_pos()):
                        screen.blit(select,selrect)
                random_enclenche_rect.centerx = 473
                random_enclenche_rect.centery = 489
                if random_enclenche_rect.collidepoint(pygame.mouse.get_pos()):
                    screen.blit(random_enclenche, (random_enclenche_rect[0],random_enclenche_rect[1]))
                pygame.display.update()
                
                # Listen for events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.MOUSEBUTTONUP:
                        for clickable in where_to_click:
                            # Case of direct action: play the move and load the board new
                            if clickable[1] :
                                tk_position = clickable[0]
                                selrect.centerx = tk_position[0]
                                selrect.centery = tk_position[1]
                                if selrect.collidepoint(pygame.mouse.get_pos()):
                                    print(f"playing direct action {clickable}")
                                    if Game.phase() == 1:
                                        Game.play(clickable[2], 1)
                                        Game.next_phase()
                                    else:
                                        Game.play(((-1,-1), clickable[2], (-1,-1), None), 2)
                                    plateau, _ = load_png("board.png")
                                    board_to_do = True
                                    pygame.time.wait(5)
                                
                            # Case of indirect action :
                            else:
                                tk_position = clickable[0]
                                selrect.centerx = tk_position[0]
                                selrect.centery = tk_position[1]
                                if selrect.collidepoint(pygame.mouse.get_pos()):
                                    print(f"playing indirect action {clickable}")
                                    # register the source and enter a choice loop
                                    source_of_alternatives = clickable[2]
                                    board_to_do = True
                                    pygame.time.wait(10)
                                    loop = 4
                        # If button RANDOM_MOVE, play a random move
                        if random_enclenche_rect.collidepoint(pygame.mouse.get_pos()):
                            Game.play_random()
                            plateau, _ = load_png("board.png")
                            board_to_do = True
                            pygame.time.wait(5)
                            break

        # game_over loop
        if loop == 3:
            screen.fill((0,70,0))
            
            # Display the winner
            winner = Game.winner
            if winner == 1:
                who = "White"
            elif winner == -1:
                who = "Black"
            pygame.time.wait(5)
            font3 = pygame.font.Font(None, 100)
            who_won = font3.render(f"{who} won !", True, (150,255,100), None)
            plateau.set_alpha(50)
            screen.blit(plateau,(0,0))
            screen.blit(who_won,(80,90))
            
            # Display the play_again button
            screen.blit(play_libre, play_libre_rect)

            # Check for collisions
            if play_libre_rect.collidepoint(pygame.mouse.get_pos()):
                screen.blit(play_encl, play_libre_rect)
            pygame.display.update()

            for event in pygame.event.get():
                # If Event QUIT, quit
                if event.type == pygame.QUIT:
                    running = False
                # If Play button, go to game phase
                if event.type == pygame.MOUSEBUTTONUP:
                    if play_libre_rect.collidepoint(pygame.mouse.get_pos()):
                        Game = Moon([[0]*7,[0]*7],gone_to_phase_2=False,nb_w=6,nb_b=6,player=1)
                        board_to_do = True
                        alternatives = []
                        source_of_alternatives = None
                        plateau, _ = load_png("board.png")
                        loop = 2

        # choice loop
        if loop == 4:
            screen.fill((0,0,0))

            # Render the game screen : played tokens, nb of remaining tokens, current player
            font1 = pygame.font.Font(None, 55)
            font2 = pygame.font.Font(None, 45)
            phase = font4.render(f'Phase {Game.phase()}', True, (30,170,0), None)
            b_count = font1.render(f'{Game.nb_b}', True, (100,255,0), None)
            w_count = font1.render(f'{Game.nb_w}', True, (100,255,0), None)
            plateau.blit(b_count,counters_positions[0])
            plateau.blit(w_count,counters_positions[1])
            plateau.blit(phase,(accueil_rect.centerx - 40, accueil_rect.centery - 255))
            if Game.player == 1:
                player = font2.render("White playing", True, (30,170,0), None)
            else : 
                player = font2.render("Black playing", True, (30,170,0), None)
            plateau.blit(player, (20,495))
            screen.blit(plateau,(0,0))
            pygame.display.flip()
            
            # Display the board
            if board_to_do:
                [outrow,inrow] = Game.state
                for i, case in enumerate(outrow):
                    if case == 1:
                        plateau.blit(white, (token_positions[0][i][0]-18, token_positions[0][i][1]-18))    
                    elif case == -1 :
                        plateau.blit(black, (token_positions[0][i][0]-18, token_positions[0][i][1]-18))
                for i, case in enumerate(inrow):
                    if case == 1:
                        plateau.blit(white, (token_positions[1][i][0]-18, token_positions[1][i][1]-18))    
                    elif case == -1 :
                        plateau.blit(black, (token_positions[1][i][0]-18, token_positions[1][i][1]-18))
                pygame.display.update()
                board_to_do = False
            
            # recover all possible actions from the source
            actions_set = actions_from_source(source_of_alternatives, Game)
            
            # Display the selected token
            if selection_to_do:
                source_position = token_positions[source_of_alternatives[0]][source_of_alternatives[1]]
                selectedrect.centerx = source_position[0]
                selectedrect.centery = source_position[1]
                selrect.centerx = source_position[0]
                selrect.centery = source_position[1]
                plateau.blit(selected, selectedrect)
                plateau.blit(select, selrect)
                screen.blit(plateau,(0,0))
                pygame.display.update()
                selection_to_do = False
                print("Set of possibles choices (actions_set):")
                print(actions_set)
            
            # Listen for collisions
            for action in actions_set:
                position = action[0]
                selrect.centerx = position[0]
                selrect.centery = position[1]
                if selrect.collidepoint(pygame.mouse.get_pos()):
                    screen.blit(select,selrect)            
            pygame.display.flip()
            pygame.time.wait(10) 

            # Listen for events
            for event in pygame.event.get():
                # If Event QUIT, quit
                if event.type == pygame.QUIT:
                    running = False
                # If Event BUTTONUP:
                if event.type == pygame.MOUSEBUTTONUP:
                    voidclick = True
                    # si on est dans zone clicable simple: faire l'action simple,
                    for action in actions_set:
                        selrect.centerx = action[0][0]
                        selrect.centery = action[0][1]
                        if selrect.collidepoint(pygame.mouse.get_pos()):
                            voidclick = False
                            # direct action
                            if not action[1]:
                                print(f"trying to choose un-ambiguous : {action}")
                                Game.play(action[3], 2)
                                Game.next_phase()
                                plateau, _ = load_png("board.png")
                                source_of_alternatives = None
                                board_to_do = True
                                selection_to_do = True
                                loop = 2
                                pygame.time.wait(5)

                            # ambiguous action
                            else:
                                print("ambiguous choice")
                                alternatives.append(action[3][0])
                                alternatives.append(action[3][1])
                                selrect.centerx = action[0][0]
                                selrect.centery = action[0][1]
                                plateau.blit(select,selrect)
                                pygame.display.update()
                                loop = 5
                                break
                    if voidclick:
                        source_of_alternatives = None
                        selection_to_do = True
                        board_to_do = True
                        loop = 2
                        plateau, _ = load_png("board.png")

        # 2nd choice loop
        if loop == 5:
            pygame.event.poll()
            left = pygame.mouse.get_pos()[0] <= screen_size/2
            screen.blit(plateau,(0,0))

            act_left = alternatives[0][0]
            act_right = alternatives[1][0]
            text_left = alternatives[0][1]
            text_right = alternatives[1][1]

            fogleft = pygame.Surface((int(screen_size/2), screen_size), SRCALPHA)
            fogleft.fill((255,255,255,255))
            fogright = pygame.Surface((int(screen_size/2), screen_size), SRCALPHA)
            fogright.fill((255,255,255,255))
            
            print_left = font2.render(text_left, True, (0,0,100,200), None)
            fogleft.blit(print_left, (fogleft.get_rect().centerx - int(font2.size(text_left)[0]/2), fogleft.get_rect().centery - 100))
            print_right = font2.render(text_right, True, (0,0,100,200), None)
            fogright.blit(print_right, (fogright.get_rect().centerx - int(font2.size(text_right)[0]/2), fogright.get_rect().centery - 100))
            
            if left:
                fogright.set_alpha(0)
                fogleft.set_alpha(150)
            else:
                fogleft.set_alpha(0)
                fogright.set_alpha(150)

            screen.blit(fogleft, (0,0))
            screen.blit(fogright, (int(screen_size/2),0))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONUP:
                    if left:
                        print(text_left)
                        print(f"will play action : {act_left}")
                        Game.play(act_left, 2)
                        plateau, _ = load_png("board.png")
                        selection_to_do = True
                        source_of_alternatives = None
                        alternatives = []
                        board_to_do = True
                        loop = 2
                    else:
                        print(text_right)
                        print(f"will play action : {act_right}")
                        Game.play(act_right, 2)
                        plateau, _ = load_png("board.png")
                        selection_to_do = True
                        source_of_alternatives = None
                        alternatives = []
                        board_to_do = True
                        loop = 2
                      
    
    pygame.quit()

if __name__=='__main__':
    main()
    

    