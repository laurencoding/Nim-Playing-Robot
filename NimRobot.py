from robotdefs import *

touch,S2,color_sensor,distance_sensor=Sensors("touch",None,"color","us")
Wait(2)
Ma=Motors("a")
Mb=Motors("b")
Mc=Motors("c")

def read_state():

def get_robot_move(state,player):
    Q=LoadTable(filename='Q_data.json')

    if not state in Q:
        action=random_choice(valid_moves(state,player))
    else:
        action=top_choice(Q[state])

    return action

def make_move(state,move):
    move=[pile,sticks]
    # move to location of correct pile and whenever there is a spike
    
    move_piece()


g=Game(number_of_games=1)
g.run(Q1_agent,human_agent)
Remember(Q1_agent.Q,filename='Q1_data.json')

# Play Game!

player=1
while True:
    wait_for_turn() 

    read_state()

    state=read_state()   

    move=get_robot_move(state,player)
    # if this doesn't work
    # move=random_move(state,player)
    make_move(state,move)    

    new_state=update_state(state,player,move)

    status=win_status(state,player)

    if status=='win':
        do_victory_dance()   
        break
    elif status=='lose':
        do_sad_dance()    
        break
    else:
        pass

Shutdown()

