#!/usr/bin/python3
import pygame
import sys
import os
import random
import string
import shutil
import subprocess
import math
import zipfile

# Initialize Pygame
pygame.init()

# Constants
CANVAS_WIDTH, CANVAS_HEIGHT = 256, 192
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (232, 51, 48)  # E83330
BLUE = (48, 4, 245)  # 3004F5
ORANGE = (251, 97, 0)  # FB6100
FRAME_COUNTER_COLOR = (255, 82, 0)  # FF5200
TOOLBAR_HEIGHT = 70
WINDOW_WIDTH, WINDOW_HEIGHT = CANVAS_WIDTH, CANVAS_HEIGHT + TOOLBAR_HEIGHT
BRUSH_SIZE = 3  # Default draw tool size
UNDO_STACK_SIZE = 10
MAX_FRAMES = 500
DEFAULT_SPEED = 29.9275  # Frames per second
WHITE_BRUSH_SIZE = 8  # Brush size for white color
CURSOR_COLOR = (52, 52, 52)  # #343434
MAX_VOLUME = 0.1  # Maximum volume for the drawing sound
DRAW_SOUND = pygame.mixer.Sound("sound/DRAW.wav")  # Load the drawing sound
SAVE_SOUND = pygame.mixer.Sound("sound/SAVE.wav")  # Load the save sound
OPEN_SOUND = pygame.mixer.Sound("sound/OPEN.wav")  # Load the open sound


# Load images for the third color button
red_button_img = pygame.image.load('assets/red.png')
blue_button_img = pygame.image.load('assets/blue.png')
    
# Track the last red/blue color used for each frame
last_red_blue_color = RED

# Vars
copied_frame = None  # Initialize copied_frame variable
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Pynote Studio')  # Updated window title

# Load custom font
font_path = 'assets/font.otf'  # Make sure the font file is in the same directory
font = pygame.font.Font(font_path, 16)  # Reduced font size for "Erase" text

# Load sounds
sounds = {
    "OPEN": pygame.mixer.Sound("sound/OPEN.wav"),
    "COLOUR": pygame.mixer.Sound("sound/COLOUR.wav"),
    "ERASE": pygame.mixer.Sound("sound/ERASE.wav"),
    "FRAME_LEFT": pygame.mixer.Sound("sound/FRAME_LEFT.wav"),
    "NEW_FRAME": pygame.mixer.Sound("sound/NEW_FRAME.wav"),
    "FRAME_RIGHT": pygame.mixer.Sound("sound/FRAME_RIGHT.wav"),
    "BLOCK": pygame.mixer.Sound("sound/BLOCK.wav"),
    "PLAY": pygame.mixer.Sound("sound/PLAY.wav"),
    "STOP": pygame.mixer.Sound("sound/STOP.wav"),
    "SAVE": pygame.mixer.Sound("sound/SAVE.wav"),
    "TOOL": pygame.mixer.Sound("sound/TOOL.wav"),
    "RMFRAME": pygame.mixer.Sound("sound/REMOVEPAGE.wav"),
    "CFRAME": pygame.mixer.Sound("sound/COPYPAGE.wav"),
    "PFRAME": pygame.mixer.Sound("sound/PASTEPAGE.wav"),
    "BACK": pygame.mixer.Sound("sound/BACK.wav")
}

# Load images
images = {
    "PEN": pygame.image.load("assets/pen.png"),
    "ERASER": pygame.image.load("assets/eraser.png"),
    "ERASEBUTTON": pygame.image.load("assets/erasebutton.png"),
    "FRAME_L": pygame.image.load("assets/frame_l.png"),
    "FRAME_R": pygame.image.load("assets/frame_r.png"),
    "STOP": pygame.image.load("assets/stop.png"),
    "PLAY": pygame.image.load("assets/play.png"),
    "BLANK": pygame.image.load("assets/blank.png"),
    "RED": pygame.image.load("assets/red.png"),
    "BLUE": pygame.image.load("assets/blue.png"),
    "THIRDCOLORBTN": pygame.image.load("assets/third_color_button.png"),
}

# Play startup sound
sounds["OPEN"].play()

# Create frame list and initial canvas
frames = [pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA)]
frames[0].fill(WHITE)
current_frame = 0
is_playing = False
playback_speed = DEFAULT_SPEED  # Default playback speed

# Initial state
drawing = False
color = BLACK
undo_stack = [frames[current_frame].copy()]

# Color palette for each frame
frame_colors = {
    BLACK: BLACK,
    WHITE: WHITE,
    RED: RED
}
# Function to draw the toolbar
def draw_toolbar():
    # Skip drawing static parts of the toolbar while user is painting
    if drawing == False or color == WHITE:
        pygame.draw.rect(screen, ORANGE, (0, CANVAS_HEIGHT, WINDOW_WIDTH, TOOLBAR_HEIGHT))
    
        # Draw color buttons with images
        screen.blit(images["PEN"], (10, CANVAS_HEIGHT + 10))
        screen.blit(images["ERASER"], (40, CANVAS_HEIGHT + 10))
        pygame.draw.rect(screen, BLACK, (70, CANVAS_HEIGHT + 10, 20, 20), 2)  # Red/Blue color selector outline
        pygame.draw.rect(screen, WHITE, (70, CANVAS_HEIGHT + 10, 20, 20))  # Red/Blue color selector background
    
        # Draw Erase button with image
        erase_button_img = images["ERASEBUTTON"]
        erase_button_rect = erase_button_img.get_rect(topleft=(100, CANVAS_HEIGHT + 10))
        screen.blit(erase_button_img, erase_button_rect)
    
        # Draw frame navigation buttons with images
        frame_left_img = images["FRAME_L"]
        frame_left_rect = frame_left_img.get_rect(topleft=(170, CANVAS_HEIGHT + 10))
        screen.blit(frame_left_img, frame_left_rect)
        frame_right_img = images["FRAME_R"]
        frame_right_rect = frame_right_img.get_rect(topleft=(210, CANVAS_HEIGHT + 10))
        screen.blit(frame_right_img, frame_right_rect)

        # Draw Play/Stop button with image overlay
        play_stop_img = images["STOP"] if is_playing else images["PLAY"]
        play_stop_img_rect = play_stop_img.get_rect(center=(130, CANVAS_HEIGHT + 50))
        screen.blit(play_stop_img, play_stop_img_rect)

        # Draw Export button with blank image
        export_button_img = images["BLANK"]
        export_button_rect = export_button_img.get_rect(topleft=(170, CANVAS_HEIGHT + 40))
        screen.blit(export_button_img, export_button_rect)

        # Draw Export text with smaller font size
        export_text = font.render('Export', True, ORANGE)
        export_text = pygame.transform.scale(export_text, (int(export_text.get_width() * 0.8), int(export_text.get_height() * 0.8)))
        screen.blit(export_text, (177, CANVAS_HEIGHT + 43))

        # Draw third color button with dynamic image
        if color == RED:
            color_button_img = images["RED"]
        elif color == BLUE:
            color_button_img = images["BLUE"]
        else:
            color_button_img = images["THIRDCOLORBTN"]
        screen.blit(color_button_img, (70, CANVAS_HEIGHT + 10))

    # Draw frame number text
    frame_text = font.render(f'{current_frame + 1} / {len(frames)}', True, FRAME_COUNTER_COLOR)
    screen.blit(frame_text, (WINDOW_WIDTH - frame_text.get_width() - 10, 5))


# Function to get the current speed option
def get_current_speed_option():
    for option, speed in SPEED_OPTIONS.items():
        if speed == playback_speed:
            return option
    return "N/A"

# Function to save the current state to the undo stack
def save_state():
    if len(undo_stack) >= UNDO_STACK_SIZE:
        undo_stack.pop(0)
    undo_stack.append(frames[current_frame].copy())

# Function to handle erase
def erase():
    sounds["ERASE"].play()
    frames[current_frame].fill(WHITE)

# Function to draw the cursor overlay
def draw_cursor_overlay(x, y):
    if color == WHITE and y < CANVAS_HEIGHT:
        screen_refresh()
        pygame.draw.rect(screen, CURSOR_COLOR, (x - WHITE_BRUSH_SIZE // 2, y - WHITE_BRUSH_SIZE // 2, WHITE_BRUSH_SIZE, WHITE_BRUSH_SIZE), 1)

# Function to switch between red and blue
def switch_color():
    global color, last_red_blue_color
    sounds["COLOUR"].play()
    if color == RED:
        color = BLUE
        last_red_blue_color = BLUE
        replace_color(RED, BLUE)
    else:
        color = RED
        last_red_blue_color = RED
        replace_color(BLUE, RED)

# Function to replace all occurrences of a color with another color in the current frame
def replace_color(old_color, new_color):
    for y in range(CANVAS_HEIGHT):
        for x in range(CANVAS_WIDTH):
            if frames[current_frame].get_at((x, y))[:3] == old_color:
                frames[current_frame].set_at((x, y), new_color + (frames[current_frame].get_at((x, y))[3],))

# Function to navigate frames
def navigate_frames(direction):
    global current_frame, frames
    if direction == 'left':
        if current_frame == 0:
            sounds["BLOCK"].play()
        else:
            current_frame = max(current_frame - 1, 0)
            sounds["FRAME_LEFT"].play()
    elif direction == 'right':
        if current_frame < len(frames) - 1:
            current_frame += 1
            sounds["FRAME_RIGHT"].play()
        else:
            if len(frames) < MAX_FRAMES:
                frames.append(pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT), pygame.SRCALPHA))
                current_frame += 1
                frames[current_frame].fill(WHITE)
                sounds["NEW_FRAME"].play()
            else:
                sounds["BLOCK"].play()

# Function to play frames
def play_frames():
    global is_playing, current_frame
    is_playing = True
    sounds["PLAY"].play()
    clock = pygame.time.Clock()
    while is_playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if 100 <= x <= 160 and CANVAS_HEIGHT + 40 <= y <= CANVAS_HEIGHT + 60:
                    is_playing = False
                    sounds["STOP"].play()
                    return
            elif event.type == pygame.KEYDOWN:
                if pygame.K_1 <= event.key <= pygame.K_8:
                    option = int(pygame.key.name(event.key))
                    set_speed_option(option)
                    sounds["TOOL"].play()
        if current_frame >= len(frames) - 1:
            current_frame = 0
        else:
            current_frame += 1
        screen.fill(WHITE)
        screen.blit(frames[current_frame], (0, 0))
        draw_toolbar()
        pygame.display.flip()
        clock.tick(playback_speed)

# Function to set the playback speed option
def set_speed_option(option):
    global playback_speed
    if option in SPEED_OPTIONS:
        playback_speed = SPEED_OPTIONS[option]

# Function to check for color conflicts
def check_color_conflict(x, y):
    if color == RED or color == BLUE:
        red_present = blue_present = False
        for px in range(max(0, x - BRUSH_SIZE // 2), min(CANVAS_WIDTH, x + BRUSH_SIZE // 2)):
            for py in range(max(0, y - BRUSH_SIZE // 2), min(CANVAS_HEIGHT, y + BRUSH_SIZE // 2)):
                px_color = frames[current_frame].get_at((px, py))[:3]
                if px_color == RED:
                    red_present = True
                elif px_color == BLUE:
                    blue_present = True
                if red_present and blue_present:
                    raise Exception("Cannot draw red on a frame with blue.")
        print("No color conflict detected.")

# Function to handle drawing on the canvas
def handle_drawing(x, y):
    global color
    if y < CANVAS_HEIGHT:
        red_present = is_color_present(RED)
        blue_present = is_color_present(BLUE)
        if color == RED and blue_present:
            color = BLUE
        elif color == BLUE and red_present:
            color = RED
        pygame.draw.rect(frames[current_frame], color, (x - BRUSH_SIZE // 2, y - BRUSH_SIZE // 2, BRUSH_SIZE, BRUSH_SIZE))

# Function to show the export progress window using Pygame
def show_export_progress(progress):
    progress_screen = pygame.display.set_mode((300, 100))
    progress_screen.fill(WHITE)
    pygame.display.set_caption("Export Progress")
    progress_label = font.render(f"Exporting frame {progress + 1} of {len(frames)}", True, BLACK)
    progress_screen.blit(progress_label, (50, 40))
    pygame.display.flip()
    return progress_screen

# Function to generate a random filename
def generate_filename():
    random_numbers1 = ''.join(random.choices(string.digits, k=3))
    random_letters = ''.join(random.choices(string.ascii_uppercase, k=6))
    random_numbers2 = ''.join(random.choices(string.digits, k=3))
    random_numbers3 = ''.join(random.choices(string.digits, k=4))
    return f"{random_numbers1}{random_letters}_{random_numbers2}0{random_letters[1]}{random_numbers2}X{random_numbers2}0{random_numbers1}0{random_numbers3}XXXX0_000.mp4"

# Function to export frames
def export_frames():
    sounds["SAVE"].play()
    if not os.path.exists("frames"):
        os.makedirs("frames")

    for idx, frame in enumerate(frames):
        progress_screen = show_export_progress(idx)
        pygame.image.save(frame, f"frames/frame_{idx:04d}.png")

    # Use ffmpeg to create a video from the frames
    subprocess.run([
        "ffmpeg", "-y", "-framerate", str(playback_speed), "-i", "frames/frame_%04d.png", 
        "-pix_fmt", "yuv420p", generate_filename()
    ])

    # Delete the frames folder
    shutil.rmtree("frames")

    # Close the progress window
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Pynote Studio')

# Function to enforce color replacement rule if both red and blue are found on the same frame
def enforce_color_rule():
    red_found = False
    blue_found = False
    for y in range(CANVAS_HEIGHT):
        for x in range(CANVAS_WIDTH):
            px_color = frames[current_frame].get_at((x, y))[:3]
            if px_color == RED:
                red_found = True
            elif px_color == BLUE:
                blue_found = True
            if red_found and blue_found:
                break
        if red_found and blue_found:
            break
    if red_found and blue_found:
        replace_color(BLUE, RED)

# Function to play the drawing sound
def play_draw_sound():
    if not pygame.mixer.get_busy():  # Check if any sound is currently playing
        DRAW_SOUND.play(loops=-1)  # Start playing the drawing sound continuously

# Function to stop the drawing sound
def stop_draw_sound():
    DRAW_SOUND.stop()  # Stop playing the drawing sound

# Function to check if a specific color is present in the current frame
def is_color_present(color):
    for y in range(CANVAS_HEIGHT):
        for x in range(CANVAS_WIDTH):
            if frames[current_frame].get_at((x, y))[:3] == color:
                return True
    return False

def screen_refresh():
    screen.fill(WHITE)
    screen.blit(frames[current_frame], (0, 0))
    draw_toolbar()

def screen_refresh_draw():
    screen.blit(frames[current_frame], (0, 0))
    draw_toolbar()

# Function to remove the current frame
def remove_frame():
    global current_frame, frames
    if len(frames) > 1:
        sounds["RMFRAME"].play()
        frames.pop(current_frame)
        if current_frame >= len(frames):
            current_frame = max(0, current_frame - 1)
    else:
        sounds["BLOCK"].play()

# Function to copy the current frame
def copy_frame():
    global copied_frame
    copied_frame = frames[current_frame].copy()
    sounds["CFRAME"].play()

# Function to paste the copied frame
def paste_frame():
    global copied_frame
    if copied_frame:
        frames[current_frame] = copied_frame.copy()
        sounds["PFRAME"].play()
        screen_refresh()

# Function to save the project
def save_project():
    sounds["SAVE"].play()

    # Create the temp_frames directory if it doesn't exist
    if not os.path.exists('.temp_frames'):
        os.makedirs('.temp_frames')

    # Generate a random filename
    filename = 'rawflipnote.rawppm'

    # Create a zip archive
    with zipfile.ZipFile(filename, 'w') as project_zip:
        for idx, frame in enumerate(frames):
            frame_filename = f'FRAME{idx+1:03d}.JPG'
            frame_path = os.path.join('.temp_frames', frame_filename)
            pygame.image.save(frame, frame_path)
            project_zip.write(frame_path, arcname=frame_filename)
            os.remove(frame_path)  # Clean up temporary frame file
    
    # Delete the temp_frames folder
    shutil.rmtree('.temp_frames')

# Function to open a project
def open_project():
    sounds["SAVE"].play()

    # Create the temp_frames directory if it doesn't exist
    if not os.path.exists('.temp_frames'):
        os.makedirs('.temp_frames')

    global frames, current_frame
    with zipfile.ZipFile('rawflipnote.rawppm', 'r') as project_zip:
        frames = []
        for file in sorted(project_zip.namelist()):
            if file.endswith('.JPG'):
                frame = pygame.image.load(project_zip.open(file))
                frames.append(frame)
    current_frame = 0
    screen_refresh()

    # Delete the temp_frames folder
    shutil.rmtree('.temp_frames')
    
# Event handling loop
running = True
previous_pos = None  # Track previous mouse position
# Control framerate
fps_clock = pygame.time.Clock()

# Initial screen render
screen_refresh()

while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = event.pos
                if y < CANVAS_HEIGHT:
                    drawing = True
                    save_state()
                    handle_drawing(x, y)
                    enforce_color_rule()
                    screen_refresh_draw()
                    play_draw_sound()  # Start playing the drawing sound continuously
                elif CANVAS_HEIGHT <= y < CANVAS_HEIGHT + TOOLBAR_HEIGHT:
                    # Handle toolbar button clicks
                    if 10 <= x <= 30 and CANVAS_HEIGHT + 10 <= y <= CANVAS_HEIGHT + 30:
                        color = BLACK
                        sounds["COLOUR"].play()
                        screen_refresh()
                    elif 40 <= x <= 60 and CANVAS_HEIGHT + 10 <= y <= CANVAS_HEIGHT + 30:
                        color = WHITE
                        sounds["COLOUR"].play()
                        screen_refresh()
                    elif 70 <= x <= 90 and CANVAS_HEIGHT + 10 <= y <= CANVAS_HEIGHT + 30:
                        switch_color()
                        enforce_color_rule()
                        screen_refresh()
                    elif 100 <= x <= 160 and CANVAS_HEIGHT + 10 <= y <= CANVAS_HEIGHT + 30:
                        erase()
                        enforce_color_rule()
                        screen_refresh()
                    elif 170 <= x <= 200 and CANVAS_HEIGHT + 10 <= y <= CANVAS_HEIGHT + 30:
                        navigate_frames('left')
                        screen_refresh()
                    elif 210 <= x <= 240 and CANVAS_HEIGHT + 10 <= y <= CANVAS_HEIGHT + 30:
                        navigate_frames('right')
                        screen_refresh()
                    elif 100 <= x <= 160 and CANVAS_HEIGHT + 40 <= y <= CANVAS_HEIGHT + 60:
                        if is_playing:
                            is_playing = False
                            sounds["STOP"].play()
                        else:
                            play_frames()
                        screen_refresh()
                    elif 170 <= x <= 230 and CANVAS_HEIGHT + 40 <= y <= CANVAS_HEIGHT + 60:
                        export_frames()
                        screen_refresh()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                previous_pos = None  # Reset previous position
                stop_draw_sound()  # Stop playing the drawing sound when mouse is released
                screen_refresh()
        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                x, y = event.pos
                if y < CANVAS_HEIGHT:
                    # Draw a line from previous position to current position
                    if previous_pos:
                        current_brush_size = WHITE_BRUSH_SIZE if color == WHITE else BRUSH_SIZE
                        pygame.draw.line(frames[current_frame], color, previous_pos, (x, y), current_brush_size)
                        # Removed by IC - fixed program locking up while drawing - How is this needed? You cannot change the color while drawing.
                        #enforce_color_rule()  # Enforce the color rule on mouse motion
                        screen_refresh_draw()
                    # Calculate mouse movement speed
                    if previous_pos:
                        distance = math.sqrt((x - previous_pos[0]) ** 2 + (y - previous_pos[1]) ** 2)
                        max_distance = 5
                        volume = min(distance / max_distance * MAX_VOLUME, MAX_VOLUME)  # Adjust volume based on distance
                        DRAW_SOUND.set_volume(volume)  # Set the volume of the drawing sound
                    previous_pos = (x, y)  # Update previous position
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                remove_frame()
                screen_refresh()
            elif event.key == pygame.K_b:
                switch_color()
                enforce_color_rule()
                screen_refresh()
            elif event.key == pygame.K_x:
                erase()
                enforce_color_rule()
                screen_refresh()
            elif event.key == pygame.K_LEFT:
                navigate_frames('left')
                screen_refresh()
            elif event.key == pygame.K_RIGHT:
                navigate_frames('right')
                screen_refresh()
            elif event.key == pygame.K_e:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    export_frames()
                    screen_refresh()
            elif event.key == pygame.K_c:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    copy_frame()
            elif event.key == pygame.K_v:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    paste_frame()
            elif event.key == pygame.K_s:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    save_project()
            elif event.key == pygame.K_o:
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    open_project()

    draw_cursor_overlay(mouse_x, mouse_y)
    pygame.display.flip()
    fps_clock.tick(60)

# Done! Time to quit.
pygame.quit()
sys.exit()
