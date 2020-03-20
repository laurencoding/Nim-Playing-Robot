from Robot373 import *
from Game import *
from classy import *
import os
import numpy as np
from numpy import s_
from pylab import imread,array,repeat,newaxis,imsave
from scipy.signal import find_peaks

Ma=Motors("a")
Mb=Motors("b")
Mc=Motors("c")

# definitions for game
def initial_state():
    state=Board (1,4)
    return state

def print_state(state):
    print("Pile 0:",state[0])
    print("Pile 1:",state[1])
    print("Pile 2:",state[2])
    print("Pile 3:",state[3])

def valid_moves(state,player):
    moves=[]
    
    for pile in range(4):    #run through all 3 piles
        sticks=state[pile]    
        for s in range(1,sticks+1):   #run through all numbers up to max sticks in pile GREATER THAN 0??
            move=[pile,s]
            moves.append(move)
    return moves        
        

def update_state(state,player,move):
    new_state=state
    pile,sticks=move
    new_state[pile]=state[pile]-sticks 
    return new_state

def win_status(state,player):

    if state[0]==0 and state[1]==0 and state[2]==0 and state[3]==0:
        return 'win'
    elif state[0]==1 and state[1]==0 and state[2]==0 and state[3]==0:
        return 'lose'
    elif state[0]==0 and state[1]==1 and state[2]==0 and state[3]==0:
        return 'lose'
    elif state[0]==0 and state[1]==0 and state[2]==1 and state[3]==0:
        return 'lose'
    elif state[0]==0 and state[1]==0 and state[2]==0 and state[3]==1:
        return 'lose'

def random_move(state,player):
    move=random_choice(valid_moves(state,player))
    return move

human_agent=Agent(human_move)
random_agent=Agent(random_move)

def Q_move(state,player,info):
    Q=info.Q
    last_action=info.last_action
    last_state=info.last_state
    
    alpha=info.alpha  # learning rate
    gamma=info.gamma  # memory 
    epsilon=info.epsilon  # probability of doing random move
    
    if not state in Q:
        Q[state]=Table()
        for action in valid_moves(state,player):
            Q[state][action]=0.0
            
    if random.random()<epsilon:  # random move
        action=random_choice(Q[state])
    else:
        action=top_choice(Q[state])
        
        
    if not last_action is None:  # anything but the first move
        r=0.0
        Q[last_state][last_action]+=alpha*(r + 
            gamma*max([Q[state][a] for a in Q[state]]) -
            Q[last_state][last_action] )
        
    return action

def Q_post(status,player,info):
    Q=info.Q
    last_action=info.last_action
    last_state=info.last_state
    
    alpha=info.alpha  # learning rate
    gamma=info.gamma  # memory 
    epsilon=info.epsilon  # probability of doing random move

    if status=='lose':
        r=-1.0
    elif status=='win':
        r=1.0
    else:
        r=0.0
        
    if not last_action is None:  # anything but the first move
        Q[last_state][last_action]+=alpha*(r -
            Q[last_state][last_action] )
        

Q1_agent=Agent(Q_move)
Q1_agent.post=Q_post

Q1_agent.alpha=0  # learning rate
Q1_agent.gamma=0.9  # memory
Q1_agent.epsilon=0  # chance of making a random move

# definitions for robot#########################################################################################
def buttonpress(touch):
    while not touch.value:
        Wait(0.1)
    while touch.value:
        Wait(0.1)

def forward(power):
    Ma.power=-power
    Mb.power=-power

def backward(power):
    Ma.power=power
    Mb.power=power

def stop():
    Ma.power=0
    Mb.power=0
    Mc.power=0

def end_to_start():
    stop()
    backward(30)
    Wait(4.8)
    stop()

def move_piece():
    Mc.power=-30
    Wait(0.4)
    stop()
    Mc.power=30
    Wait(0.39)
    stop()

def reset_counts():
    pile=0
    sticks=0

def init_sensors():
    color_sensor=Sensors2(None,None,"color",None)

    color=None
    print("Waiting for color sensor to behave...")
    Wait(3)
    while color is None:
        color=color_sensor.value
        Wait(0.05)
    print("done.")

    return color_sensor


def get_robot_move(state,player):
    Q=LoadTable(filename='Q_data.json')

    if not state in Q:
        action=random_choice(valid_moves(state,player))
    else:
        action=top_choice(Q[state])

    return action

def wait_for_turn(buttonpress):
    print("Press the button when it's my turn.")
    buttonpress(touch)

def do_victory_dance():
    print("Yay! I won!")
    Ma.power=0    
    Mb.power=-50
    Wait(1)
    stop()
    forward(50)  
    backward(50)
    Wait(1)
    Ma.power=-50
    Mb.power=0
    Wait(1)
    stop()
    forward(50)
    backward(50)
    Wait(1)
    stop()

def do_sad_dance():
    print("Boo... I lost..")
    backward(10)
    Wait(3)
    stop()
    Ma.power=30
    Wait(2.5)
    stop()


##################################################################################################################
#from ai373#


def read_image(fname,crop=None):  # crop=s_[30:260,45:310]
    if crop is None:
        raise ValueError('Crop info not given.  Call like read_image("blah.jpg",s_[30:260,45:310])')

    arr=imread(fname)
    print("Min and Max",arr.min(),arr.max())    
    
    if np.any(arr>1):  # if the image is read in as uint8, it's not 0-1 but 0-255, so scale it down
        print("Min and Max",arr.min(),arr.max())
        print("Scaling it down....")
        arr=arr/255
        print("Min and Max",arr.min(),arr.max())    
        
    if len(arr.shape)>2 and arr.shape[2]>3:  # alpha channel
        print("arr shape",arr.shape)
        print("Removing alpha channel")
        arr=arr[:,:,:3]
        print("new arr shape",arr.shape)
        
        
    arr=arr[crop]  # change this for your image
    
    return arr


def get_square(arr,Nr,Nc,r,c,percent=100):
    image_rows,image_cols=arr.shape[:2]
    square_row=int(image_rows/Nr)
    square_col=int(image_cols/Nc)
    
    start_row=int(r*square_row)
    end_row=int((r+1)*square_row)

    start_col=int(c*square_col)
    end_col=int((c+1)*square_col)
    
    if percent==100:
        square=arr[start_row:end_row,start_col:end_col]
        
    else:
        dc=int((end_col-start_col)*(100-percent)/2.0/100.0)
        dr=int((end_row-start_row)*(100-percent)/2.0/100.0)

        square=arr[start_row+dr:end_row-dr,start_col+dc:end_col-dc]
        
        
    return square

def get_square_size(arr,Nr,Nc,r,c,size=None):
    image_rows,image_cols=arr.shape[:2]
    square_row=int(image_rows/Nr)
    square_col=int(image_cols/Nc)

    start_row=int(r*square_row)
    end_row=int((r+1)*square_row)

    start_col=int(c*square_col)
    end_col=int((c+1)*square_col)

    if size is None:
        square=arr[start_row:end_row,start_col:end_col]
    else:
        start_row=int(start_row+(end_row-start_row)/2.0-size[0]/2.0)
        start_col=int(start_col+(end_col-start_col)/2.0-size[1]/2.0)

        square=arr[start_row:start_row+size[0],start_col:start_col+size[1]]


    return square

from Game import Board
#from imageio import imwrite
#from glob import glob


def images_to_vectors(im,verbose=True):
    data_all=image.images_to_vectors(im,verbose=verbose)
    if np.any(data_all.vectors>1):
        if verbose:
            print("\nScaling down...")

        data_all.vectors/=255.0
        if verbose:
            summary(data_all)

    return data_all

def array_to_image_struct(arr):
    if isinstance(arr,list):
        N=len(arr)
        data=Struct()
        data.DESCR="Images"
        data.files=[None]*N
        data.data=arr
        data.targets=[0]*N
        data.target_names=['None']*N
        
        
    else:
        data=Struct()
        data.DESCR="Images"
        data.files=[None]
        data.data=[arr]
        data.targets=[0]
        data.target_names=['None']

    return data

