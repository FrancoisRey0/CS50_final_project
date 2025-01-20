from PIL import Image
import os

pixel_positions = [[(24,6), (40,13), (44,30), (33, 44), (15,44), (4,30), (8,13)],
                       [(24,34), (18,31), (17,24), (21,19), (28,19), (32,24), (31,31)]]
phase_position = (45,5)
player_position = (3,3)

def show_state(state, player, phase):
    """Creates a 50x50 PIL image (bmp) of a state (list of two lists of 7 values in {-1,0,1}) and show it."""
    img = Image.new(mode="L", size=(50,50), color=50) 
    for i in range(2):
        for j in range(7):
            position = pixel_positions[i][j]
            positions = [position, 
                         (position[0], position[1] +1),
                         (position[0] + 1, position[1]), 
                         (position[0] + 1, position[1] + 1)]
            if state[i][j] == 0:
                for pos in positions:
                    img.putpixel(pos,120)
            elif state[i][j] == -1:
                for pos in positions:
                    img.putpixel(pos,0)
            elif state[i][j] == 1:
                for pos in positions:
                    img.putpixel(pos,255)
    if player == 1:
        img.putpixel(player_position,255)
    else:
        img.putpixel(player_position,0)
    
    if phase == 1:
        for i in range(3):
            img.putpixel((44,5+i),255)
    if phase == 2:
        for i in range(3):
            img.putpixel((44,5+i),255)
        for i in range(3):
            img.putpixel((46,5+i),255)
    img.show()

def print_and_register(state, player, phase, title):
    """Creates a 50x50 PIL image of a state (list of two lists of 7 values in {-1,0,1})
    and register it as a bitmap under the name title.bmp."""

    img = Image.new(mode="L", size=(50,50), color=50)
    for i in range(2):
        for j in range(7):
            position = pixel_positions[i][j]
            positions = [position, 
                         (position[0], position[1] +1),
                         (position[0] + 1, position[1]), 
                         (position[0] + 1, position[1] + 1)]
            if state[i][j] == 0:
                for pos in positions:
                    img.putpixel(pos,120)
            elif state[i][j] == -1:
                for pos in positions:
                    img.putpixel(pos,0)
            elif state[i][j] == 1:
                for pos in positions:
                    img.putpixel(pos,255)
    if player == 1:
        img.putpixel(player_position,255)
    else:
        img.putpixel(player_position,0)
    
    if phase == 1:
        for i in range(3):
            img.putpixel((44,5+i),255)
    if phase == 2:
        for i in range(3):
            img.putpixel((44,5+i),255)
        for i in range(3):
            img.putpixel((46,5+i),255)

    dir_path = os.path.join(os.getcwd(), "repertory")
    os.makedirs(dir_path, exist_ok=True)  # Creates the directory if it doesn't exist
    path = os.path.join(dir_path, title +".bmp")
    img.save(path)

state = [[1,1,1,1,1,1,1],[-1,-1,-1,-1,0,0,0]]
player = -1
phase = 1
test = (state,player,phase)
show_state(*test)
print_and_register(*test,"test")
