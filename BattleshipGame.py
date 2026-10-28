######################### 
# Author: HornStrikeLabs
# Date: 2026-10-27
#########################
import pygame
import sys
import numpy as np
import string
import random

#Functions
#Makes the board with the wave in each spot
class BattleshipGame:
   def __init__(self):
       self.player_ships = []
       self.comp_ships = []
       self.Ship_Lengths = [5,4,3,3,2]
       
       self.player_primary_board = self.create_board()
       self.player_tracking_board = self.create_board()
       self.comp_primary_board = self.create_board()
       
       self.game_state = "SHIP_PLACEMENT"
       self.status_message = "Welcome to Battleship!"
       
       self.placement_index = 0
       self.placement_orientation = 'H'
       
       self.start_row = None
       self.start_col = None
       
       for length in self.Ship_Lengths:
           self.comp_ships.append(self.place_ship_randomly(self.comp_primary_board, length))
           
   def draw_board(self, surface, board, top_left_x, top_left_y, cell_size=40, show_ships=False, mouse_pos=None):
       font = pygame.font.SysFont(None, 24)
       for r in range(10):
            for c in range(10):
    
                x = top_left_x + c * cell_size
                y = top_left_y + r * cell_size
                rect = pygame.Rect(x, y, cell_size, cell_size)
    
                # HOVER HIGHLIGHT
                if mouse_pos:
                    mx, my = mouse_pos
                    if rect.collidepoint(mx, my):
                        pygame.draw.rect(surface, (255, 255, 0), rect, 3)
    
                        # SHIP PLACEMENT PREVIEW
                        if self.game_state == "SHIP_PLACEMENT":
                            row, col = r, c
                            ship_len = self.Ship_Lengths[self.placement_index]
    
                            # Compute preview coords
                            if self.placement_orientation == 'H':
                                coords = [(row, col+i) for i in range(ship_len)]
                            else:
                                coords = [(row+i, col) for i in range(ship_len)]
    
                            # Check validity
                            valid = True
                            for rr, cc in coords:
                                if rr > 9 or cc > 9 or board[rr, cc] != '~':
                                    valid = False
                                    break
    
                            # Draw preview
                            color = (0, 255, 0) if valid else (255, 0, 0)
                            for rr, cc in coords:
                                if 0 <= rr < 10 and 0 <= cc < 10:
                                    px = top_left_x + cc * cell_size
                                    py = top_left_y + rr * cell_size
                                    pygame.draw.rect(surface, color,
                                                     (px, py, cell_size, cell_size), 3)
    
                # DRAW BASE CELL
                pygame.draw.rect(surface, (255, 255, 255), rect, 1)
                cell = board[r, c]
                if cell == 'S' and show_ships:
                    pygame.draw.rect(surface, (0, 100, 200), rect)
                if cell == 'X':  # Hit
                    pygame.draw.line(surface, (255, 0, 0), (x, y),
                                     (x+cell_size, y+cell_size), 3)
                    pygame.draw.line(surface, (255, 0, 0), (x+cell_size, y),
                                     (x, y+cell_size), 3)
                if cell == 'M':  # Miss
                    pygame.draw.circle(surface, (200, 200, 200),
                                       rect.center, cell_size//4)
           
   def create_board(self):
       return np.full((10,10), '~', dtype='U1')
   
   def handle_ship_placement_click(self, row, col):
        ship_len = self.Ship_Lengths[self.placement_index]
    
        # Compute coords
        if self.placement_orientation == 'H':
            coords = [(row, col+i) for i in range(ship_len)]
        else:
            coords = [(row+i, col) for i in range(ship_len)]
    
        # Validate
        for r, c in coords:
            if r > 9 or c > 9 or self.player_primary_board[r, c] != '~':
                return  # invalid placement
    
        # Place ship
        for r, c in coords:
            self.player_primary_board[r, c] = 'S'
    
        self.player_ships.append(coords)
        self.placement_index += 1
        
        if self.placement_index >= len(self.Ship_Lengths):
            self.game_state = "PLAYER_TURN"
            self.status_message = "All ships placed! Your turn."
        
   def place_ship_randomly(self, board, ship_len):
        while True:
            orientation = random.choice(['H', 'V'])
            start_row = random.randint(0, 9)
            start_col = random.randint(0, 9)
    
            if orientation == 'H':
                if start_col + ship_len <= 10:
                    if np.all(board[start_row, start_col:start_col + ship_len] == '~'):
                        coords = [(start_row, c) for c in range(start_col, start_col + ship_len)]
                        board[start_row, start_col:start_col + ship_len] = 'S'
                        return coords
    
            else:  # Vertical
                if start_row + ship_len <= 10:
                    if np.all(board[start_row:start_row + ship_len, start_col] == '~'):
                        coords = [(r, start_col) for r in range(start_row, start_row + ship_len)]
                        board[start_row:start_row + ship_len, start_col] = 'S'
                        return coords 
   def handle_keypress(self, key):
       if key == pygame.K_r:
           self.placement_orientation = 'V' if self.placement_orientation == 'H' else 'H'
        
   def process_shot_and_report(self, target_board, row, col, target_spot, tracker_board=None):
        #Processes a shot, updates boards, and returns status.
        if target_spot == 'S':
            target_board[row, col] = 'X' # Mark as Hit
            if tracker_board is not None:
                tracker_board[row, col] = 'X'
            self.status_message = ">>> HIT! <<<"
        else:
            target_board[row, col] = 'M' # Mark as Miss
            if tracker_board is not None:
                tracker_board[row, col] = 'M'
            self.status_message = ">>> Miss. <<<"
    
   def check_ship_sunk(self,ship_coords, board):
        return all(board[r, c] == 'X' for r, c in ship_coords)
    
   def draw_ship_tracker(self, surface):
       title_font = pygame.font.SysFont(None, 32)
       font = pygame.font.SysFont(None, 24)
       title = title_font.render("Enemy Fleet", True, (255,255,255))
       surface.blit(title, (980,100))
       ship_names = ["Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer"]
       y = 150
       for ship, name in zip(self.comp_ships, ship_names):
           sunk = self.check_ship_sunk(ship, self.comp_primary_board)
           ship_length = len(ship)
           for i in range(ship_length):
               ship_rect = pygame.Rect(980 + i * 25,y,20,20)
               if sunk: 
                   colour = (180,0,0)
               else:
                   colour = (0, 120, 255)
                   
               pygame.draw.rect(surface,colour,ship_rect)
               pygame.draw.rect(surface, (255,255,255),ship_rect,1)
               
               if sunk:
                   pygame.draw.line(surface, (255,255,255),ship_rect.topleft,ship_rect.bottomright,2)
                   pygame.draw.line(surface,(255,255,255),ship_rect.topright,ship_rect.bottomleft,2)
           text = font.render(name,True,(255,255,255))
           surface.blit(text,(980, y + 25))
           y+= 65        
                   
   def check_win(self, board):
        """Checks if any 'S' (unsunk ship parts) remain on the board."""
        return 'S' not in board

   def handle_player_shot(self, row, col):
    if self.game_state in ("PLAYER_WON","COMPUTER_WON"):
        return
    if self.game_state != "PLAYER_TURN":
        return
    # Prevent shooting the same place twice
    if self.player_tracking_board[row, col] in ('X', 'M'):
        self.status_message = "You already fired there."
        return
    target_spot = self.comp_primary_board[row, col]
    # Apply hit/miss to both boards
    self.process_shot_and_report(self.comp_primary_board, row, col, target_spot, self.player_tracking_board)
    sunk_ship = False

    # Check if a ship was sunk
    if target_spot == 'S':
        for ship in self.comp_ships:
            if (row, col) in ship:
                if self.check_ship_sunk(ship, self.comp_primary_board):
                    self.status_message = ">>> You sunk an enemy ship! <<<"
                    sunk_ship = True
                break
    # Check win condition AFTER sunk message is set
    if self.check_win(self.comp_primary_board):
        self.game_state = "PLAYER_WON"
        self.status_message = "!!! VICTORY !!!"
        return
    # Only overwrite the status message if no sunk message was set
    if not sunk_ship:
        self.status_message = "Computer's turn..."
    # Switch turn
    self.game_state = "WAITING_FOR_COMPUTER"
    
   def display_board(self, board, title):
        print(title)
        print(board)
    
   def handle_computer_turn(self):
        self.status_message = "\n--- Computer's Turn ---"
        while True:
            comp_row = random.randint(0, 10 - 1)
            comp_col = random.randint(0, 10 - 1)
            
            # Check if AI has already targeted this spot
            if self.player_primary_board[comp_row, comp_col] in ['X', 'M']:
                continue
            else:
                break
                
        self.shot_coord_name = f"{string.ascii_uppercase[comp_row]}{comp_col + 1}"
        self.status_message = f"Computer fires at {self.shot_coord_name}..."
        # Define target_spot before calling process_shot_and_report
        target_spot = self.player_primary_board[comp_row, comp_col]
        self.process_shot_and_report(self.player_primary_board, comp_row, comp_col, target_spot)
        
        if target_spot == 'S':
            for ship in self.player_ships:
                if (comp_row, comp_col) in ship:
                    if self.check_ship_sunk(ship, self.player_primary_board):
                        self.status_message = ">>> The computer sunk one of your ships! <<<"    
                    break
        if self.check_win(self.player_primary_board):
            self.game_state = "COMPUTER_WON"
            self.status_message = "\n*** DEFEAT! The computer has sunk all your battleships! ***"
            return # End the game loop
        self.game_state = "PLAYER_TURN"
    
   def handle_click(self, pos):
       # Rotate button
    if self.game_state in ("PLAYER_WON","COMPUTER_WON"):
        return
    if pygame.Rect(50, 10, 120, 30).collidepoint(pos):
        self.placement_orientation = 'V' if self.placement_orientation == 'H' else 'H'
        return
    # Player board is on the left
    player_grid = self.get_grid_coords(pos, 50, 100)

    # Computer board is on the right
    comp_grid = self.get_grid_coords(pos, 550, 100)

    if self.game_state == "SHIP_PLACEMENT":
        if player_grid:
            row, col = player_grid
            self.handle_ship_placement_click(row, col)
        return

    if self.game_state == "PLAYER_TURN":
            if comp_grid:
                row, col = comp_grid
                self.handle_player_shot(row, col)
            return
            
   def get_grid_coords(self, pos, top_left_x, top_left_y, cell_size=40):
    x, y = pos
    if x < top_left_x or y < top_left_y:
        return None
    col = (x - top_left_x) // cell_size
    row = (y - top_left_y) // cell_size
    if 0 <= row < 10 and 0 <= col < 10:
        return row, col
    return None
    
   def reset_game(self):
    # Reset boards
    self.player_primary_board = self.create_board()
    self.player_tracking_board = self.create_board()
    self.comp_primary_board = self.create_board()

    # Reset ships
    self.player_ships = []
    self.comp_ships = []
    self.Ship_Lengths = [5, 4, 3, 3, 2]

    # Reset placement
    self.placement_index = 0
    self.placement_orientation = 'H'

    # Reset game state
    self.game_state = "SHIP_PLACEMENT"
    self.status_message = "Game restarted! Place your ships."

    # Reset AI memory
    self.comp_shot_memory = []
    self.comp_targets = []
    self.comp_last_hit = None

    # Reset win/lose flags
    self.game_over = False

    # Place computer ships randomly
    for length in self.Ship_Lengths:
        self.comp_ships.append(self.place_ship_randomly(self.comp_primary_board, length))
        
    #---Main Game Execution---
pygame.init()
BASE_WIDTH = 1200
BASE_HEIGHT = 600
SCREEN_WIDTH = BASE_WIDTH
SCREEN_HEIGHT = BASE_HEIGHT

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.RESIZABLE)
game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
clock = pygame.time.Clock()
game = BattleshipGame()

cell_size = 40
reset_button = pygame.Rect(200, 10, 120, 30)
rotate_button = pygame.Rect(50, 10, 120, 30)

computer_delay_start = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            SCREEN_WIDTH = event.w
            SCREEN_HEIGHT = event.h
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game.placement_orientation = ('V' if game.placement_orientation == 'H' else 'H')
                game.status_message = f"Orientation: {game.placement_orientation}"

        # MOUSE CLICK HANDLING
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            mx = int(mx * BASE_WIDTH / SCREEN_WIDTH)
            my = int(my * BASE_HEIGHT / SCREEN_HEIGHT)
            #Reset Button
            if reset_button.collidepoint(mx, my):
                print("Restart button clicked!")
                game.reset_game()
                continue
            
            #Rotate Button
            if rotate_button.collidepoint(mx, my):
                game.placement_orientation = ('V' if game.placement_orientation == 'H' else 'H')
                game.status_message = f"Orientation: {game.placement_orientation}"
                continue

            # Ship placement clicks (left board)
            if game.game_state == "SHIP_PLACEMENT":
                grid = game.get_grid_coords((mx,my), 50, 100)
                if grid: 
                    row, col = grid
                    game.handle_ship_placement_click(row, col)

            # Player shooting clicks (right board)
            elif game.game_state == "PLAYER_TURN":
                grid = game.get_grid_coords((mx, my), 550,100)
                if grid:
                    row, col = grid
                    game.handle_player_shot(row, col)
                    if game.game_state == "WAITING_FOR_COMPUTER":
                        computer_delay_start = pygame.time.get_ticks()

    # COMPUTER TURN
    if game.game_state == "WAITING_FOR_COMPUTER":
        print("Waiting for computer...")
        if computer_delay_start is not None:
            print("Timer exists")
            
            if pygame.time.get_ticks() - computer_delay_start >= 1500:  # 2 seconds
                print("AI should fire now")
                game.handle_computer_turn()
                computer_delay_start = None
                if game.game_state not in ("PLAYER_WON","COMPUTER_WON"):
                    game.game_state = "PLAYER_TURN"  # or whatever comes next
                    
    # DRAW EVERYTHING
    screen.fill((0,0,0))
    game_surface.fill((0,0,0))
    mouse_pos = pygame.mouse.get_pos()
    mouse_pos = (int(mouse_pos[0] * BASE_WIDTH / SCREEN_WIDTH),int(mouse_pos[1] * BASE_HEIGHT/ SCREEN_HEIGHT))
    
    # Reset button
    pygame.draw.rect(game_surface, (80, 80, 80), reset_button)
    pygame.draw.rect(game_surface, (255, 0, 0), reset_button, 2)
    font = pygame.font.SysFont(None, 32)
    text = font.render("Restart", True, (255, 255, 255))
    game_surface.blit(text, (reset_button.x + 10, reset_button.y + 5))

    #Rotate Button
    pygame.draw.rect(game_surface, (80, 80, 80), rotate_button)
    text = font.render("Rotate (R)", True, (255, 255, 255))
    game_surface.blit(text, (rotate_button.x + 10, rotate_button.y + 5))

    # Player board (left)
    label_font = pygame.font.SysFont(None, 40)
    player_label = label_font.render("Your Fleet", True, (255,255,255))
    enemy_label = label_font.render("Enemy Waters", True, (255,255,255))
    
    game_surface.blit(player_label, (50,65))
    game_surface.blit(enemy_label, (550,65))
    game.draw_board(game_surface, game.player_primary_board, 50, 100,
                    show_ships=True, mouse_pos=mouse_pos)

    # Tracking board (right)
    game.draw_board(game_surface, game.player_tracking_board, 550, 100, show_ships=False, mouse_pos=mouse_pos)
    
    # Draw sunk ship tracker
    game.draw_ship_tracker(game_surface)

    text = font.render(game.status_message, True, (255, 255, 255))
    game_surface.blit(text, (50, 540))
    scaled_surface = pygame.transform.smoothscale(game_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface,(0,0))
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
