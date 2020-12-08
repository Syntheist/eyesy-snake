import pygame
import random
import time

def setup(screen, etc):
    '''
    eyesy runs this setup fx regardless so may as well init things here
        https://www.critterandguitari.com/manual?m=EYESY_Manual
    
    globals feel gross but it didn't detect the mode when I wrapped it in a class
        to use self so whatever
    '''

    # make setup vars work elsewhere because I can't wrap this in a class :c
    global color_black, color_primary, color_secondary, color_info
    global snake_size, first_tick, last_tick, snake_max_length, snake_body
    global last_input, start_x, start_y, food_x, food_y, knob_test

    # color definitions
    color_black = (0, 0, 0)
    color_primary = (204, 255, 204)
    color_secondary = (255, 102, 102)
    color_info = (102, 102, 255)

    # snake size based off of screen size
    snake_size = etc.yres/10

    # pick random starting positions based off of screen size
    start_x = int(random.randrange(0, etc.xres, snake_size))
    start_y = int(random.randrange(0, etc.yres, snake_size))
    food_x = random.randrange(0, etc.xres, snake_size)
    food_y = random.randrange(0, etc.yres, snake_size)

    # snake movement tracking
    snake_location = {'x':start_x, 'y':start_y}
    snake_body = [snake_location]
    snake_max_length = 5
    
    # time
    last_tick = time.time()
    first_tick = time.time()
    
    # check knob state
    knob_test = etc.knob1
    
    # init last_input
    last_input = 'up'

def draw(screen, etc):
    '''
    this is run on a loop and flashes a single frame to the screen at its
        conclusion
        
    'etc' is the included eyesy library that does hardware things like listen
        and respond to knobs
    '''
    # globals that we need change during runtime
    global last_tick, last_input, snake_max_length
    global food_x, food_y, snake_body, knob_test, first_tick
    
    # reinit movement options for snek
    movement_options = ['up','down','left','right']
    
    # gate for detected tempo ticks to reduce false positives
    tempo_gate = round(50 + etc.knob1*50, 2)

    # get time since last tick
    time_delta = time.time() - last_tick
    game_timer = int(time.time() - first_tick)
    
    # collision check
    collision = False

    # volume threshold detection
    tempo_tick = False
    if etc.audio_in[0] > 900 and time_delta >= tempo_gate/120 - 0.09:
        tempo_tick = True
        last_tick = time.time()
    
    # draw snek
    for snake_segment in snake_body:
        pygame.draw.rect(
            screen,
            color_primary,
            (snake_segment['x'], snake_segment['y'], snake_size, snake_size))
    
    # draw food
    pygame.draw.rect(
            screen,
            color_secondary,
            (food_x, food_y, snake_size, snake_size))

    # prepare to draw text   
    font = pygame.font.SysFont("freemono", 24)
    score = font.render("snek lemnth: "+ str(snake_max_length), True, color_info)
    tempo = font.render("tempo gate: "+ str(tempo_gate), True, color_info)
    game_timer_display = font.render("time not dead: "+ str(game_timer) + 's', True, color_info)
    
    # draw that shit
    screen.blit(game_timer_display, (etc.xres/40, etc.yres/40))
    screen.blit(score, (etc.xres/40, 2*etc.yres/40))
    
    # check for knob state change
    if etc.knob1 != knob_test:
        screen.blit(tempo, (etc.xres/40, 3*etc.yres/40))

    # draw border
    pygame.draw.rect(
        screen,
        (# rectangle color
            50 + 150/(abs(etc.audio_in[0])+1),
            50 + 150/(abs(etc.audio_in[99])+1),
            50 + 150/(abs(etc.audio_in[50])+1)),
        (# rectangle position
            0, 0, etc.xres, etc.yres),
        10)

    # what to do on the beat
    if tempo_tick == True:
        # check knob state
        knob_test = etc.knob1
    
        # draw border flashes
        pygame.draw.rect(
            screen,
            (# rectangle color
                100 + 150/(abs(etc.audio_in[0])+1),
                100 + 150/(abs(etc.audio_in[99])+1),
                100 + 150/(abs(etc.audio_in[50])+1)),
            (# rectangle position
                0, 0, etc.xres, etc.yres),
            10)

        # input corrections for proximity
        for snake_segment in snake_body:
            if snake_body[-1]['x'] + snake_size == snake_segment['x']:
                try:
                    movement_options.remove('right')
                except ValueError as e:
                    pass
            if snake_body[-1]['x'] - snake_size == snake_segment['x']:
                try:
                    movement_options.remove('left')
                except ValueError as e:
                    pass
            if snake_body[-1]['y'] - snake_size == snake_segment['y']:
                try:
                    movement_options.remove('up')
                except ValueError as e:
                    pass
            if snake_body[-1]['y'] + snake_size == snake_segment['y']:
                try:
                    movement_options.remove('down')
                except ValueError as e:
                    pass
        
        # choose from remaining calid options 
        input = random.choice(movement_options)
        
        # input corrections to prevent u-turns
        if input == 'down' and last_input == 'up':
            try:
                movement_options.remove('down')
                input = random.choice(movement_options)
            except ValueError as e:
                    pass
        if input == 'up' and last_input == 'down':
            try:
                movement_options.remove('up')
                input = random.choice(movement_options)
            except ValueError as e:
                    pass
        if input == 'right' and last_input == 'left':
            try:
                movement_options.remove('right')
                input = random.choice(movement_options)
            except ValueError as e:
                    pass
        if input == 'left' and last_input == 'right':
            try:
                movement_options.remove('left')
                input = random.choice(movement_options)
            except ValueError as e:
                    pass
        
        # log input for comparisons    
        last_input = input

        # move the snek
        if input  == 'up':
            snake_body.append({
                'x': snake_body[-1]['x'],
                'y': snake_body[-1]['y'] - snake_size})
        if input  == 'down':
            snake_body.append({
                'x': snake_body[-1]['x'],
                'y': snake_body[-1]['y'] + snake_size})
        if input  == 'right':
            snake_body.append({
                'x': snake_body[-1]['x'] + snake_size,
                'y': snake_body[-1]['y']})
        if input  == 'left':
            snake_body.append({
                'x': snake_body[-1]['x'] - snake_size,
                'y': snake_body[-1]['y']})

        # check for duplicate segments after move
        for snake_segment in snake_body:
            if snake_body.count(snake_segment) > 1:
                collision = True

        # what to do if food gets picked up
        if (snake_body[-1]['x'], snake_body[-1]['y']) == (food_x, food_y):
            snake_max_length += 1
            food_x = random.randrange(0, etc.xres, snake_size)
            food_y = random.randrange(0, etc.yres, snake_size)
        
        # screen flips
        if snake_body[-1]['x'] < 0:
            snake_body[-1]['x'] = int((etc.xres/snake_size))*snake_size
        if snake_body[-1]['x'] > etc.xres:
            snake_body[-1]['x'] = 0
        if snake_body[-1]['y'] < 0:
            snake_body[-1]['y'] = int((etc.yres/snake_size)-1)*snake_size
        if snake_body[-1]['y'] > etc.yres - 10:
            snake_body[-1]['y'] = 0
            
        # what to do if snek gets too long
        if len(snake_body) >= snake_max_length:
            snake_body.pop(0)

        # check for failstate and reset
        if collision == True:
            start_x = int(random.randrange(0, etc.xres, snake_size))
            start_y = int(random.randrange(0, etc.yres, snake_size))
            snake_location = {'x':start_x, 'y':start_y}
            snake_body = [snake_location]
            snake_max_length = 5
            food_x = random.randrange(0, etc.xres, snake_size)
            food_y = random.randrange(0, etc.yres, snake_size)
            first_tick = time.time()
