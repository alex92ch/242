# Autor:            Alexander Siegenthaler
# Datum:            2023-04-21
# Titel:            Pong
# Beschreibung:     - Minigame das mit Halocode realisiert wurde
#                   - Spiellogik ist an Pong angelehnt
#                   - 2 Spieler


import mbuild, event, halo, time, random, sys

# global variables
player1 = 0
player2 = 0
gameOver = False
roundOver = False
fieldPlayer1 = None
fieldPlayer2 = None

# startup of halocode
@event.start
def on_start():
    startup()

# Halocode waits on user input to start the game
def startup():

    # startup loop, press button to start a new game
    while True:
        if halo.button.is_pressed():
                game_running()

def game_running():
    global fieldPlayer1, fieldPlayer2, gameOver

    # defines the spawn field of the ball
    # the game is running until its game over
    while not gameOver == True:
        print('game started')
        
        # a new game field for each player is generated
        randomBallPosition = random.choice([True,False])
        fieldPlayer1 = Field(16, 8, randomBallPosition,1)
        fieldPlayer2 = Field(16, 8, not randomBallPosition,2)
        # the round is running until a player scores
        round_running()
        if player1 > 9 or player2 > 9:
            gameOver = True
    sys.exit()


def round_running():
    global fieldPlayer1, fieldPlayer2, roundOver, player1, player2
    player1_lost = False
    player2_lost = False
    roundOver = False
    while not roundOver == True:
        print('round started')
        # Joystick 1 moves the paddle on the left side
        if mbuild.joystick.get_value('x', 1) < -1:
            fieldPlayer1.move_player('left')


        # Joystick 1 moves the paddle on the right side
        if mbuild.joystick.get_value('x', 1) > 1:
            fieldPlayer1.move_player('right')


        # Joystick 2 moves the paddle on the left side
        if mbuild.joystick.get_value('x', 2) < -1:
            fieldPlayer2.move_player('left')


        # Joystick 2 moves the paddle on the right side
        if mbuild.joystick.get_value('x', 2) > 1:
            fieldPlayer2.move_player('right')

        fieldPlayer1.move_ball()
        fieldPlayer2.move_ball()

        player1_lost = fieldPlayer1.check_collition()
        player2_lost = fieldPlayer2.check_collition()

        if player1_lost:
            player2 = player2 + 1
            roundOver = True

        if player2_lost:
            player1 = player1 + 1
            roundOver = True
        
        fieldPlayer1.paint()
        fieldPlayer2.paint()

        time.sleep(2)

# CLASS DEFINITIONS

class Field:
    def __init__(self, x, y, ballSpawn, playerNumber):
        self.x = x
        self.y = y
        self.playerNumber = playerNumber
        self.ball = None

        if ballSpawn:
            self.ball = Ball(random.randint(1, 16), 7)

        self.score = 0
        self.player = Player(9, 1,5)
        self.goal = Goal(9, 0)
        self.wall1 = Wall(0)
        self.wall2 = Wall(17)
        self.border = Border(9)

    def move_player(self, direction):
        # the occupied fields of the player
        player_fields = self.player.get_occupied_fields()
        # the occupied fields of the walls
        wall_fields = self.wall1.get_occupied_fields() + self.wall2.get_occupied_fields()

        # Check if any x,y pair in player_fields is the same as any x,y pair in wall_fields
        for (x, y) in player_fields:
            if (x, y) in wall_fields:
                return  # do not move the player if there is a collision with the wall
        
        if self.ball is not None:
            # the occupied fields of the ball
            ball_fields = [(self.ball.x, self.ball.y)]
            # Check if any x,y pair in player_fields is the same as any x,y pair in ball_fields
            for (x, y) in player_fields:
                if (x, y) in ball_fields:
                    return
        
        # move the player
        self.player.move(direction)

    def check_collition(self):
        if self.ball is not None:
            # the occupied fields of the player
            player_fields = self.player.get_occupied_fields()
            # the occupied fields of the walls
            wall_fields = self.wall1.get_occupied_fields() + self.wall2.get_occupied_fields()
            # the occupied fields of the ball
            ball_fields = [(self.ball.x, self.ball.y)]
            # the occupied fields of the goal

            goal_fields = self.goal.get_occupied_fields()
            # the occupied fields of the border
            border_fields = self.border.get_occupied_fields()

            for (x, y) in ball_fields:
                if (x, y) in player_fields:
                    self.ball.on_player_collision(self.player.x)
                if (x, y) in wall_fields:
                    self.ball.on_wall_collision()
                if (x, y) in goal_fields:
                    return True
                if (x, y) in border_fields:
                    self.ball.on_border_collision()
                    self.ball = None
        return False

    def move_ball(self):
        if self.ball is not None:
            self.ball.move()

    def paint(self):
        # clear the field
        mbuild.led_panel.clear(self.playerNumber)

        # paint the player
        player_fields = self.player.get_occupied_fields()

        for (x, y) in player_fields:
            mbuild.led_panel.set_pixel(x, y, True, self.playerNumber)

        # paint the ball
        if self.ball is not None:
            ball_fields = [(self.ball.x, self.ball.y)]
            for (x, y) in ball_fields:
                mbuild.led_panel.set_pixel(x, y, True, self.playerNumber)


class Player:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
    
    def get_occupied_fields(self):
        # calculate the boundaries of the occupied fields
        x_min = self.x - (self.size-1)//2
        x_max = self.x + (self.size-1)//2

        # create an array to store the occupied fields
        occupied_fields = []

        # loop through the rows and columns within the boundaries
        for row in range(x_min, x_max + 1):
            for col in range(self.y, self.y + 1):
                # add the row and column as a tuple to the occupied_fields array
                occupied_fields.append((col, row))

        return occupied_fields

    def move(self,direction):
        if direction == 'left':
            self.x -= 1
        elif direction == 'right':
            self.x += 1

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice(['top', 'down', 'top-left', 'top-right', 'down-left', 'down-right'])

    def move(self):
        if self.direction == 'top':
            self.y -= 1
        elif self.direction == 'down': 
            self.y += 1
        elif self.direction == 'top-left': 
            self.y -= 1
            self.x -= 1
        elif self.direction == 'top-right':
            self.y -= 1
            self.x += 1
        elif self.direction == 'down-left':
            self.y += 1
            self.x -= 1
        elif self.direction == 'down-right':
            self.y += 1
            self.x += 1

    def on_wall_collision(self):
        if self.direction == 'top-left':
            self.direction = 'top-right'
            self.x += 1
            self.y += 1

        if self.direction == 'down-left':
            self.direction = 'down-right'
            self.x += 1
            self.y -= 1

        if self.direction == 'top-right':
            self.direction = 'top-left'
            self.x -= 1
            self.y += 1

        if self.direction == 'down-right':
            self.direction = 'down-left'
            self.x -= 1
            self.y -= 1

    def on_border_collision(self):
        if fieldPlayer1.ball is None:
            fieldPlayer1.ball = Ball(-10, -10)
        if fieldPlayer2.ball is None:
            fieldPlayer2.ball = Ball(-10, -10)

        fieldPlayer1.ball.y -= 1
        fieldPlayer2.ball.y -= 1
        
        if self.direction == 'top':
            fieldPlayer1.ball.direction = 'down'
            fieldPlayer2.ball.direction = 'down'

        elif self.direction == 'top-right':
            fieldPlayer1.ball.x = 16 - self.x - 1
            fieldPlayer2.ball.x = 16 - self.x - 1
            fieldPlayer1.ball.direction = 'down-left'
            fieldPlayer2.ball.direction = 'down-left'

        elif self.direction == 'top-left':
            fieldPlayer1.ball.x = 16 - self.x + 1
            fieldPlayer2.ball.x = 16 - self.x + 1
            fieldPlayer1.ball.direction = 'down-right'
            fieldPlayer2.ball.direction = 'down-right'


    def on_player_collision(self,player_x):
        # determine which side of the player the ball hit
        if self.x < player_x:
            side = "left"
        elif self.x > player_x:
            side = "right"
        else:
            side = "center"
        
        # change the direction of the ball based on which side it hit
        if side == "left":
            if self.direction == "top" or self.direction == "top-left" or self.direction == "top-right":
                self.direction = "down-left"
                self.x -= 1
                self.y -= 1
            if self.direction == "down" or self.direction == "down-left" or self.direction == "down-right":
                self.direction = "top-left"
                self.x -= 1
                self.y += 1

        if side == "right":
            if self.direction == "top" or self.direction == "top-left" or self.direction == "top-right":
                self.direction = "down-right"
                self.x += 1
                self.y -= 1
            if self.direction == "down" or self.direction == "down-left" or self.direction == "down-right":
                self.direction = "top-right"
                self.x += 1
                self.y += 1

        if side == "center":
            if self.direction == "top" or self.direction == "top-left" or self.direction == "top-right":
                self.direction = "down"
                self.y -= 1
            if self.direction == "down" or self.direction == "down-left" or self.direction == "down-right":
                self.direction = "top"
                self.y += 1


class Wall:
    def __init__(self,x):
        self.x = x

    def get_occupied_fields(self):
            # calculate the boundaries of the occupied fields
            x_min = self.x
            x_max = self.x

            # create an array to store the occupied fields
            occupied_fields = []

            # loop through the rows and columns within the boundaries
            for row in range(0, 10):
                # add the row and column as a tuple to the occupied_fields array
                occupied_fields.append((17, row))

            return occupied_fields

class Border:
    def __init__(self,x):
        self.x = x
    
    def get_occupied_fields(self):
        # calculate the boundaries of the occupied fields
        x_min = 1
        x_max = 16

        # create an array to store the occupied fields
        occupied_fields = []

        # loop through the rows within the boundaries
        for x in range(x_min, x_max + 1):
            # add the x and y as a tuple to the occupied_fields array
            occupied_fields.append((x, 9))

        return occupied_fields

class Goal:
    def __init__(self,x,y=0):
        self.x = x
        self.y = y
    
    def get_occupied_fields(self):
        # calculate the boundaries of the occupied fields
        x_min = 1
        x_max = 16

        # create an array to store the occupied fields
        occupied_fields = []

        # loop through the rows within the boundaries
        for x in range(x_min, x_max + 1):
            # add the x and y as a tuple to the occupied_fields array
            occupied_fields.append((x, self.y))

        return occupied_fields