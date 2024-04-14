import os
import json
from dotenv import load_dotenv
from Challenge3_alg import manhattan_distance, a_star_search, reconstruct_path

import paho.mqtt.client as paho
from paho import mqtt
import time

import random

# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)


# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))


# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

# stores the possible moves a user can make
moveset_list = ["UP", "DOWN", "LEFT", "RIGHT"]
game_over = 0

# Determine next move given A* results
def get_move_cmd(current, next):
    dx, dy = next[0] - current[0], next[1] - current[1]
    if dx == 1:
        return "DOWN"
    elif dx == -1:
        return "UP"
    elif dy == 1:
        return "RIGHT"
    elif dy == -1:
        return "LEFT"

# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    if "Game Over" in str(msg.payload):
        global game_over  # need to use this line to edit global variable; not needed to read
        game_over += 1
        print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    if game_over == 0:
        print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    if "game_state" in msg.topic:
        time.sleep(1) # Wait a second to resolve game start

        # Load game state
        game_state = json.loads(msg.payload)

        # Get game state data
        current_position = tuple(game_state['currentPosition'])
        walls = set(tuple(wall) for wall in game_state['walls'])
        coins = game_state['coin1'] + game_state['coin2'] + game_state['coin3']
        coins = [tuple(coin) for coin in coins]

        # Select nearest coin as target
        if coins:
            target_coin = min(coins, key=lambda x: manhattan_distance(current_position, x))

            # Use A* to get nearest path
            came_from, cost_so_far = a_star_search(current_position, target_coin, walls)
            path = reconstruct_path(came_from, current_position, target_coin)

            # Determine next move
            if path:
                next_move = path[0]
                move_cmd = get_move_cmd(current_position, next_move)
                print("Moving player: ", player_name_1, " towards coin ", target_coin, " with move ", move_cmd)
                client.publish(f"games/{lobby_name}/{player_name_1}/move", move_cmd)
            # Randomize move (as backup)
            else:
                print("No path found, moving randomly.")
                bot_move = random.choice(moveset_list)
                client.publish(f"games/{lobby_name}/{player_name_1}/move", bot_move)

        time.sleep(1) # Wait a second to resolve game start


if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="PlayerB1", userdata=None, protocol=paho.MQTTv5)
    
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

    lobby_name = "BotLobby"
    player_name_1 = "B_1"
    game_over = 0

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/{player_name_1}/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'BTeam',
                                            'player_name' : player_name_1}))
    
    time.sleep(1) # Wait a second to resolve game start
    #client.publish(f"games/{lobby_name}/start", "START")
    time.sleep(3) # Wait a second to resolve game start


    client.loop_forever()