import time
import math
import random
from PIL import Image, ImageDraw
import os
from utils.text_utils import text_to_matrix, split_text_to_lines
from core.minigames.hobby import HIT_ZONE_Y, BEAT_POSITIONS, NOTE_WIDTH

class Graphics:
    def __init__(self, matrix, matrix_width, matrix_height, pixel_size):
        # 'matrix' is the LED matrix instance you use to push images (via SwapOnVSync or SetImage)
        self.matrix = matrix
        self.matrix_width = matrix_width
        self.matrix_height = matrix_height
        self.pixel_size = pixel_size
        self.position = [matrix_width // 2, matrix_height // 2]
        self.last_move_time = time.time()
        self.last_switch_time = time.time()
        self.switch_interval = random.uniform(0.5, 2.0)
        self.pause_duration = random.uniform(1, 3)
        self.sprites = []
        self.current_sprite_index = 0
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.frame_x = int(matrix_width // 18)
        self.frame_y = int(matrix_height // 10)
        self.frame_width = int(matrix_width // 1.07)
        self.frame_height = int(matrix_height // 1.17)
        self.end_start_time = None
        self.death_cause = None
        self.death_sprite_folder = None
        self.in_death_animation = False
        # Create a canvas image for drawing (width = matrix_width * pixel_size, etc.)
        self.canvas = Image.new("RGB", (matrix_width * pixel_size, matrix_height * pixel_size))
        self.draw = ImageDraw.Draw(self.canvas)

    def render_to_matrix(self):
        """Push the canvas image to the LED matrix."""
        # If you draw using pixel_size > 1, resize to matrix size
        display_image = self.canvas.resize((self.matrix.width, self.matrix.height), Image.NEAREST)
        self.matrix.SetImage(display_image.convert("RGB"))


    def draw_rect(self, x, y, w, h, fill):
        # Helper method: draw a rectangle on the canvas.
        self.draw.rectangle([x, y, x + w, y + h], fill=fill)

    def load_sprites(self, folder_path):
        sprites = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                filepath = os.path.join(folder_path, filename)
                img = Image.open(filepath).convert("RGB")
                img = img.resize((10, 10))
                sprite_matrix = [[img.getpixel((x, y)) for x in range(10)] for y in range(10)]
                sprites.append(sprite_matrix)
        if not sprites:
            raise ValueError(f"No sprites found in {folder_path}")
        return sprites

    def set_sprites(self, new_sprites):
        # Update sprites and reset the sprite index.
        self.sprites = new_sprites
        self.current_sprite_index = 0

    def switch_sprite(self):
        current_time = time.time()
        if current_time - self.last_switch_time > self.switch_interval:
            self.current_sprite_index = (self.current_sprite_index + 1) % len(self.sprites)
            self.last_switch_time = current_time
            self.switch_interval = random.uniform(0.5, 2.0)

    def update_sprites(self, states):
        # Update sprites based on the current state of life.
        sprite_folder = states.get_sprite_folder()
        self.set_sprites(self.load_sprites(sprite_folder))

    def move_sprite(self):
        current_time = time.time()
        if current_time - self.last_move_time > self.pause_duration:
            direction = random.choice(["left", "right", "up", "down"])
            if direction == "left" and self.position[0] > self.frame_x:
                self.position[0] -= 1
            elif direction == "right" and self.position[0] < self.frame_x + self.frame_width - 10:
                self.position[0] += 1
            elif direction == "up" and self.position[1] > self.frame_y:
                self.position[1] -= 1
            elif direction == "down" and self.position[1] < self.frame_y + self.frame_height - 10:
                self.position[1] += 1
            self.last_move_time = current_time
            self.pause_duration = random.uniform(1, 3)
            
    def draw_frame(self):
        # Draw the frame with outlined pixels.
        for x in range(self.frame_x, self.frame_x + self.frame_width):
            # Top line: black outline then white inner pixel.
            self.draw_rect(x * self.pixel_size, self.frame_y * self.pixel_size,
                           self.pixel_size - 2, self.pixel_size - 2, fill=(255, 255, 255))
            # Bottom line.
            self.draw_rect(x * self.pixel_size, (self.frame_y + self.frame_height - 1) * self.pixel_size,
                           self.pixel_size - 2, self.pixel_size - 2, fill=(255, 255, 255))
        for y in range(self.frame_y, self.frame_y + self.frame_height):
            # Left line.
            self.draw_rect(self.frame_x * self.pixel_size, y * self.pixel_size,
                           self.pixel_size - 2, self.pixel_size - 2, fill=(255, 255, 255))
            # Right line.
            self.draw_rect((self.frame_x + self.frame_width - 1) * self.pixel_size, y * self.pixel_size,
                           self.pixel_size - 2, self.pixel_size - 2, fill=(255, 255, 255))

    def draw_sprite_at(self, x, y, sprite_path, sprite_width=10, sprite_height=10):
        """
        Draw a single sprite at a specific position.
        
        Args:
            x (int): X position on the matrix.
            y (int): Y position on the matrix.
            sprite_path (str): Path to the sprite file.
            sprite_width (int): Width of the sprite in pixels.
            sprite_height (int): Height of the sprite in pixels.
        """
        img = Image.open(sprite_path).convert("RGB")
        img = img.resize((sprite_width, sprite_height))  # Resize to specified dimensions.
        sprite_matrix = [[img.getpixel((col, row)) for col in range(sprite_width)] for row in range(sprite_height)]
        for row_idx, row in enumerate(sprite_matrix):
            for col_idx, pixel in enumerate(row):
                if pixel != (0, 0, 0):  # Skip black pixels.
                    screen_x = (x + col_idx) * self.pixel_size
                    screen_y = (y + row_idx) * self.pixel_size
                    self.draw_rect(screen_x, screen_y, self.pixel_size - 1, self.pixel_size - 1, fill=pixel)


    def draw_frame_and_points(self, selected_point_index, states):
        """
        Draw the frame and points, with unavailable points greyed out.
        """
        self.draw_frame()

        # Define the points for various screens.
        top_points = [
            (self.frame_x + self.frame_width // 7, self.frame_y - 3),   # education
            (self.frame_x + self.frame_width // 2, self.frame_y - 3),   # job
            (self.frame_x + 6 * self.frame_width // 7, self.frame_y - 3)  # food
        ]
        bottom_points = [
            (self.frame_x + self.frame_width // 7, self.frame_y + self.frame_height ),  # social
            (self.frame_x + self.frame_width // 2, self.frame_y + self.frame_height ),  # hobby
            (self.frame_x + 6 * self.frame_width // 7, self.frame_y + self.frame_height )  # housing
        ]
        
        all_points = top_points + bottom_points
        point_screens = ["education_screen", "hobby_screen", "food_screen",  # Top row
                        "socialize_screen", "job_screen", "housing_screen"]    # Bottom row

        current_time = time.time()
        for i, (x, y) in enumerate(all_points):
            screen_name = point_screens[i]
            if states.is_screen_available(screen_name):
                # Blink the selected point if it's active; otherwise red.
                color = (255, 0, 0) if not (i == selected_point_index and int(current_time * 2) % 2 == 0) else (0, 0, 0)
            else:
                # Unavailable screen – greyed out.
                color = (100, 100, 100)
            self.draw_rect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size, fill=color)


    def draw_matrix(self, matrix, start_x, start_y):
        """
        Draw an RGB matrix at the given starting position on the canvas.
        
        Args:
            matrix (list): RGB matrix to render.
            start_x (int): X coordinate (in matrix pixels) for the top-left corner.
            start_y (int): Y coordinate (in matrix pixels) for the top-left corner.
        """
        for y, row in enumerate(matrix):
            for x, pixel in enumerate(row):
                if pixel != (0, 0, 0):  # Skip black pixels.
                    screen_x = (start_x + x) * self.pixel_size
                    screen_y = (start_y + y) * self.pixel_size
                    self.draw_rect(screen_x, screen_y, self.pixel_size - 1, self.pixel_size - 1, fill=pixel)


    def draw_sprite(self):
        sprite_matrix = self.sprites[self.current_sprite_index]
        for y, row in enumerate(sprite_matrix):
            for x, pixel in enumerate(row):
                screen_x = (self.position[0] + x) * self.pixel_size
                screen_y = (self.position[1] + y) * self.pixel_size
                self.draw_rect(screen_x, screen_y, self.pixel_size - 1, self.pixel_size - 1, fill=pixel)

    def draw_text_centered(self, text, font_path="assets/fonts/tamzen.ttf", font_size=10, color="white"):
        """
        Draws text centered on the screen, splitting long lines automatically.

        Args:
            text (str): The text to draw.
            font_path (str): Path to the font file.
            font_size (int): Font size.
            color (str or RGB tuple): Text color.
        """
        lines = split_text_to_lines(text, max_chars_per_line=12)

        line_matrices = []
        line_heights = []
        for line in lines:
            matrix = text_to_matrix(line, font_path, font_size, self.matrix_width, self.matrix_height, color)
            # Only count rows that actually have pixels
            non_empty_rows = [row for row in matrix if any(pixel != (0, 0, 0) for pixel in row)]
            line_matrices.append(non_empty_rows)
            line_heights.append(len(non_empty_rows))

        # Total height with 1px spacing between lines
        total_height = sum(line_heights) + (len(lines) - 1)

        offset_y = max((self.matrix_height - total_height) // 2, 0)

        for idx, matrix in enumerate(line_matrices):
            # Determine content width for centering
            non_empty_cols = list(zip(*matrix))
            non_empty_cols = [col for col in non_empty_cols if any(pixel != (0, 0, 0) for pixel in col)]
            content_width = len(non_empty_cols)
            offset_x = max((self.matrix_width - content_width) // 4, 0)

            for y, row in enumerate(matrix):
                for x, pixel in enumerate(row):
                    if pixel != (0, 0, 0):
                        screen_x = (offset_x + x) * self.pixel_size
                        screen_y = (offset_y + y) * self.pixel_size
                        self.draw.rectangle(
                            [screen_x, screen_y, screen_x + self.pixel_size - 1, screen_y + self.pixel_size - 1],
                            fill=color if isinstance(color, tuple) else pixel
                        )
            offset_y += line_heights[idx] + 1  # Add 1 line of spacing


    def draw_home_screen(self, selected_point_index, states):
        """
        Draw the home screen, including the frame and flashing points.
        Unavailable games are greyed out.
        """
        self.clear_screen()
        self.draw_frame_and_points(selected_point_index, states)
        self.switch_sprite()
        self.move_sprite()
        self.draw_sprite()

    def render_individual_screen(self, screen_name):
        """
        Render the individual game or activity screen based on the screen name.
        """
        self.clear_screen()
        text = screen_name.replace('_', '\n').capitalize()
        text_matrix = text_to_matrix(
            text, "assets/fonts/tamzen.ttf", 11, self.matrix_width, self.matrix_height
        )

        # Draw the text in the center of the screen using the canvas.
        for y, row in enumerate(text_matrix):
            for x, pixel in enumerate(row):
                if pixel != (0, 0, 0):
                    screen_x = x * self.pixel_size
                    screen_y = y * self.pixel_size
                    self.draw_rect(screen_x, screen_y, self.pixel_size - 1, self.pixel_size - 1, fill=pixel)


    def draw_education_screen(self, selected_suitcase):
        """
        Render the education mini-game screen.
        """
        self.clear_screen()

        # Suitcase positions
        suitcase_1_x = self.matrix_width // 6
        suitcase_2_x = (self.matrix_width * 4) // 6
        suitcase_y = self.matrix_height // 2

        # Arrow positions
        arrow_y = suitcase_y - 10  # Ten rows above the suitcase
        arrow_offset = 3

        # Draw suitcases
        self.draw_sprite_at(suitcase_1_x, suitcase_y, "assets/sprites/suitcase.png", sprite_width=14, sprite_height=10)
        self.draw_sprite_at(suitcase_2_x, suitcase_y, "assets/sprites/suitcase.png", sprite_width=14, sprite_height=10)

        # Draw arrow above selected suitcase
        arrow_x = suitcase_1_x + arrow_offset if selected_suitcase == 0 else suitcase_2_x + arrow_offset
        self.draw_sprite_at(arrow_x, arrow_y, "assets/sprites/arrow.png", sprite_width=8, sprite_height=5)


    def draw_education_animation(self, selected_suitcase, animation_frame, level, loan):
        """
        Render the animation after selecting a suitcase.

        Args:
            selected_suitcase (int): Index of the selected suitcase (0 or 1).
            animation_frame (int): Current animation frame (0, 1, or 2).
            level (str): Selected education level (e.g., "BSc").
            loan (int): Associated student loan amount.
        """
        self.clear_screen()

        # Positions
        suitcase_1_x = self.matrix_width // 6
        suitcase_2_x = (self.matrix_width * 4) // 6
        suitcase_y = self.matrix_height // 2
        center_x = self.matrix_width // 2
        center_y = self.matrix_height // 2

        if animation_frame == 0:
            # Frame 1: Arrow and non-selected suitcase disappear
            selected_x = suitcase_1_x if selected_suitcase == 0 else suitcase_2_x
            self.draw_sprite_at(selected_x, suitcase_y, "assets/sprites/suitcase.png", sprite_width=14, sprite_height=10)

        elif animation_frame == 1:
            # Frame 2: Move selected suitcase to center and grow
            suitcase_size = 18  # Larger suitcase size
            self.draw_sprite_at(
                center_x - suitcase_size // 2,
                center_y - suitcase_size // 2,
                "assets/sprites/suitcase.png",
                sprite_width=suitcase_size,
                sprite_height=suitcase_size,
            )

        elif animation_frame == 2:
            # Frame 3: Display text for education level and loan
            font_path = "assets/fonts/tamzen.ttf"
            font_size = 12

            # Level text
            level_matrix = text_to_matrix(f"{level}", font_path, font_size, self.matrix_width, 10)
            self.draw_matrix(level_matrix, center_x - self.matrix_width // 4, center_y - 12)

            # Loan text
            loan_matrix = text_to_matrix(f"-${loan}", font_path, font_size, self.matrix_width, 10)
            self.draw_matrix(loan_matrix, center_x - self.matrix_width // 2, center_y + 2)


    def draw_platformer_screen(self, tama_position, platforms, goal_position):
        """
        Render the platformer mini-game screen.

        Args:
            tama_position (tuple): (x, y) position of the Tamagotchi.
            platforms (list): List of platform positions [(x1, y1, width), ...].
            goal_position (tuple): (x, y) position of the goal pixel.
        """
        self.clear_screen()

        # Draw platforms
        for platform in platforms:
            platform_x, platform_y, platform_width = platform
            for x in range(platform_width):
                self.draw_rect(
                    (platform_x + x) * self.pixel_size,
                    platform_y * self.pixel_size,
                    self.pixel_size,
                    self.pixel_size,
                    fill=(255, 255, 255)  # White platform
                )

        # Draw the goal
        goal_x, goal_y = goal_position
        self.draw_rect(
            goal_x * self.pixel_size,
            goal_y * self.pixel_size,
            self.pixel_size,
            self.pixel_size,
            fill=(0, 255, 0)  # Green goal
        )

        # Draw Tamagotchi sprite
        tama_x, tama_y = tama_position
        self.draw_sprite_at(tama_x, tama_y, "assets/sprites/tama.png", sprite_width=5, sprite_height=5)

    def draw_social_screen(self, player_sprites, other_tama_sprite, social_state):
        """
        Render the socializing mini-game screen with animations and dynamic bubble colors.
        """
        self.clear_screen()

        # Tama positions
        player_tama_x = 10
        player_tama_y = self.matrix_height // 2 + 3 + social_state["tama_animation_offset"]
        other_tama_x = self.matrix_width - 18
        other_tama_y = self.matrix_height // 2 + 3 + social_state["tama_animation_offset"]

        # Up/down animation during feedback
        if social_state["interaction_done"]:
            if social_state["animation_frames"] % 10 < 5:
                social_state["tama_animation_offset"] = -1
            else:
                social_state["tama_animation_offset"] = 1
        else:
            social_state["tama_animation_offset"] = 0

        # Draw Tamas
        self.draw_matrix(player_sprites[0], player_tama_x, player_tama_y)  # Player Tama
        self.draw_sprite_at(other_tama_x, other_tama_y, other_tama_sprite, sprite_width=10, sprite_height=10)  # Other Tama

        # Draw speech bubbles
        self.draw_rect(
            (other_tama_x - 7) * self.pixel_size,
            (other_tama_y - 4) * self.pixel_size,
            9 * self.pixel_size,
            6 * self.pixel_size,
            fill=social_state["other_bubble_color"]
        )
        self.draw_rect(
            (player_tama_x + 7) * self.pixel_size,
            (player_tama_y - 4) * self.pixel_size,
            9 * self.pixel_size,
            6 * self.pixel_size,
            fill=social_state["player_bubble_color"]
        )

        # Draw feedback sprites
        if social_state["player_feedback_sprite"]:
            feedback_index = (social_state["animation_frames"] // 10) % len(social_state["player_feedback_sprite"])
            self.draw_sprite_at(
                player_tama_x - 3,
                player_tama_y - 3,
                social_state["player_feedback_sprite"][feedback_index],
                sprite_width=6,
                sprite_height=6
            )

        if social_state["other_feedback_sprite"]:
            feedback_index = (social_state["animation_frames"] // 10) % len(social_state["other_feedback_sprite"])
            self.draw_sprite_at(
                other_tama_x + 3,
                other_tama_y - 3,
                social_state["other_feedback_sprite"][feedback_index],
                sprite_width=6,
                sprite_height=6
            )

        if not social_state["interaction_done"]:
            # Use the wiggled percentage values
            player_chance_text = f"{social_state['player_displayed_chance']}%"
            other_chance_text = f"{social_state['other_displayed_chance']}%"
            font_path = "assets/fonts/tamzen.ttf"
            font_size = 11

            # Convert to matrix form
            player_chance_matrix = text_to_matrix(
                player_chance_text, font_path, font_size, self.matrix_width, 10
            )
            other_chance_matrix = text_to_matrix(
                other_chance_text, font_path, font_size, self.matrix_width, 10
            )

            # Draw above the Tamas
            self.draw_matrix(
                player_chance_matrix,
                player_tama_x - 5,
                player_tama_y - 16  # a bit higher above the Tama
            )
            self.draw_matrix(
                other_chance_matrix,
                other_tama_x - 8,
                other_tama_y - 16
            )

        # Increment animation frames
        social_state["animation_frames"] += 1


    def draw_housing_screen(self, housing_state):
        current_house = housing_state["housing_options"][housing_state["current_choice"]]
        self.clear_screen()

        if housing_state["current_home"]:
            # ✅ Show current home status
            home_matrix = text_to_matrix("Home", "assets/fonts/tamzen.ttf", 10, self.matrix_width, self.matrix_height)
            self.draw_matrix(home_matrix, self.matrix_width // 2 - len(home_matrix[0]) // 5, (self.matrix_height // 4) - 10)
            self.draw_sprite_at(
                self.matrix_width // 4 - 5,
                self.matrix_height // 4,
                current_house["sprite"],
                sprite_width=48,
                sprite_height=24,
            )

        elif housing_state["pending"]:
            # Show "Pending" message
            pending_text = "Pending..."
            pending_matrix = text_to_matrix(pending_text, "assets/fonts/tamzen.ttf", 10, self.matrix_width, self.matrix_height)
            self.draw_matrix(pending_matrix, self.matrix_width // 2 - len(pending_matrix[0]) // 2, self.matrix_height // 2 - 10)

            # 🏠 Draw Real Estate Agent (otherTama)
            agent_x = self.matrix_width - 12  # Bottom-right corner
            agent_y = self.matrix_height - 12
            self.draw_sprite_at(agent_x, agent_y, housing_state["real_estate_agent"]["sprite"], sprite_width=10, sprite_height=10)

        else:
            # Get the current house
            house_name = current_house["name"]

            # Draw the house sprite
            self.draw_sprite_at(
                self.matrix_width // 4 - 5,
                self.matrix_height // 4,
                current_house["sprite"],
                sprite_width=48,
                sprite_height=24,
            )

            # Display house details
            text = f"{house_name}"
            text_matrix = text_to_matrix(text, "assets/fonts/tamzen.ttf", 10, self.matrix_width, self.matrix_height)
            self.draw_matrix(text_matrix, self.matrix_width // 2 - len(text_matrix[0]) // 2 + 2, -2)

    def draw_housing_reaction_game(self, housing_state, fps):
        """
        Render the different phases of the housing reaction game with animated feedback.
        """
        self.clear_screen()

        if housing_state["countdown_active"] or housing_state["random_timeout_active"]:
            # Display countdown timer.
            countdown_number = max(0, int(housing_state["countdown_timer"]))
            countdown_matrix = text_to_matrix(
                str(countdown_number), "assets/fonts/tamzen.ttf", 20, self.matrix_width, self.matrix_height
            )
            self.draw_matrix(countdown_matrix, self.matrix_width // 2 - 5, self.matrix_height // 2 - 10)

        elif housing_state["reaction_active"]:
            # Display "APPLY" prompt.
            reaction_text = "APPLY"
            reaction_matrix = text_to_matrix(
                reaction_text, "assets/fonts/tamzen.ttf", 14, self.matrix_width, self.matrix_height
            )
            self.draw_matrix(reaction_matrix, self.matrix_width // 4, self.matrix_height // 4)

        elif housing_state["reaction_result"] is not None:
            # Display Pass/Fail result.
            print("reaction_result", housing_state["reaction_result"])
            result_text = "SUCCESS" if housing_state["reaction_result"] == "pass" else "FAILED"
            result_matrix = text_to_matrix(
                result_text, "assets/fonts/tamzen.ttf", 14, self.matrix_width, self.matrix_height
            )
            self.draw_matrix(result_matrix, self.matrix_width // 4 - 8, self.matrix_height // 4)

            # Handle animated tick/cross sprites.
            animation_frame = int(time.time() * 1000 / 200) % 5  # Loop: 0, 1, 2, 3, 4.
            if animation_frame == 4:
                sprite_index = 2
            else:
                sprite_index = min(3, animation_frame + 1)

            sprite_prefix = "tick" if housing_state["reaction_result"] == "pass" else "cross"
            sprite_path = f"assets/sprites/{sprite_prefix}{sprite_index}.png"
            sprite_width, sprite_height = 12, 12

            # Draw the left sprite.
            self.draw_sprite_at(
                self.matrix_width // 2 + 8,
                self.matrix_height // 2 + 2,
                sprite_path,
                sprite_width=sprite_width,
                sprite_height=sprite_height,
            )

            # Draw the right sprite.
            self.draw_sprite_at(
                self.matrix_width // 4 - 7,
                self.matrix_height // 4 - 7,
                sprite_path,
                sprite_width=sprite_width,
                sprite_height=sprite_height,
            )


    def draw_hobby_screen(self, hobby_state):
        """
        Draws the rhythm-based hobby game.
        """
        if hobby_state is None:
            return

        self.clear_screen()

        # Draw hit zones for 3 buttons (left, center, right).
        for x_pos in BEAT_POSITIONS:
            self.draw_rect(
                x_pos * self.pixel_size,
                HIT_ZONE_Y * self.pixel_size,
                NOTE_WIDTH * self.pixel_size,
                self.pixel_size,
                fill=(255, 255, 255)
            )

        # Draw falling beats.
        for beat in hobby_state["beats"]:
            color = (0, 255, 0) if beat["hit"] else (255, 0, 0)
            self.draw_rect(
                beat["x"] * self.pixel_size,
                beat["y"] * self.pixel_size,
                NOTE_WIDTH * self.pixel_size,
                self.pixel_size,
                fill=color
            )

        # Display only the score number at the top-left.
        score_text = str(hobby_state['score'])
        highscore_text = str(hobby_state['high_score'])
        score_matrix = text_to_matrix(score_text, "assets/fonts/tamzen.ttf", 12, self.matrix_width, self.matrix_height)
        highscore_matrix = text_to_matrix(highscore_text, "assets/fonts/tamzen.ttf", 12, self.matrix_width, self.matrix_height)
        self.draw_matrix(score_matrix, 1, 0)
        self.draw_matrix(highscore_matrix, 1, 9)

        # Draw "Game Over" if the player missed too many beats.
        if hobby_state["game_over"]:
            game_over_matrix = text_to_matrix("Game Over", "assets/fonts/tamzen.ttf", 12, self.matrix_width, self.matrix_height)
            self.draw_matrix(game_over_matrix, self.matrix_width // 6 - 5, self.matrix_height // 2 + 1)


    def draw_job_feedback(self, job_state):
        """
        Render job feedback by drawing an animated tick (if pass) or cross (if fail)
        in the center of the screen.
        """
        animation_frame = int(time.time() * 1000 / 200) % 5  # Loop: 0,1,2,3,4.
        if animation_frame == 4:
            sprite_index = 2
        else:
            sprite_index = min(3, animation_frame + 1)
        
        sprite_prefix = "tick" if job_state["phase"] == "feedback_success" else "cross"
        sprite_path = f"assets/sprites/{sprite_prefix}{sprite_index}.png"
        sprite_width, sprite_height = 20, 20

        # Calculate center position in matrix coordinates.
        center_matrix_x = (self.matrix_width - (sprite_width // self.pixel_size)) // 3
        center_matrix_y = (self.matrix_height - (sprite_height // self.pixel_size)) // 4

        self.draw_sprite_at(
            center_matrix_x,
            center_matrix_y,
            sprite_path,
            sprite_width=sprite_width,
            sprite_height=sprite_height
        )


    def draw_job_screen(self, job_state):
        PRE_ANIMATION_DELAY = 0.5
        """
        Render the job minigame screen.
        Always draw three desk items at fixed positions.
        If in the "display" phase, animate the desk item if it is the next task in the sequence.
        If in the "input_animation" phase, animate the desk item corresponding to the player's last input.
        For feedback phases, fill the screen with a solid color.
        """
        self.clear_screen()

        # Feedback phases: fill the entire screen with the appropriate color
        if job_state["phase"] in ["feedback_success", "feedback_failure"]:
            self.draw_job_feedback(job_state)
            return

        phase_elapsed = time.time() - job_state["phase_start_time"]

        # For each desk item index (0, 1, 2) always draw a sprite
        for task in range(3):
            # Calculate static base positions for each desk item
            base_x = (self.matrix_width // 5) + (task * 16)
            base_y = self.matrix_height // 2 - (task % 2) * 10

            animate = False
            # Determine whether to animate this desk item:
            if job_state["phase"] == "display":
                current_index = job_state.get("current_animation_index", 0)
                if current_index < len(job_state["sequence"]) and job_state["sequence"][current_index] == task:
                    if phase_elapsed >= PRE_ANIMATION_DELAY:
                        animate = True
            elif job_state["phase"] == "input_animation":
                if "last_input" in job_state and job_state["last_input"] == task:
                    animate = True

            # Draw either an animated version or the static version.
            if animate:
                # Create a wiggle & scale effect (oscillates over a period of 1 second)
                t = time.time() % 1.0
                offset = int(math.sin(t * 2 * math.pi) * 2)  # Oscillates ±2 pixels
                scale_factor = 1.0 + 0.1 * math.sin(t * 2 * math.pi)
                animated_width = max(1, int(10 * scale_factor))
                animated_height = max(1, int(10 * scale_factor))
                animated_x = base_x - (animated_width - 10) // 2 + offset
                animated_y = base_y - (animated_height - 10) // 2 + offset
                item_path = job_state["items"][task]  # Use the sprite corresponding to this desk position
                self.draw_sprite_at(animated_x, animated_y, item_path, sprite_width=animated_width, sprite_height=animated_height)
            else:
                # Draw the static desk item.
                item_path = job_state["items"][task]
                self.draw_sprite_at(base_x, base_y, item_path, sprite_width=10, sprite_height=10)

    def draw_button(self, label_matrix, x_pos, selected, button_y):
        button_width = len(label_matrix[0])
        button_height = len(label_matrix)
        screen_y = button_y

        # Draw background
        bg_color = (255, 255, 255) if selected else (0, 0, 0)
        self.draw.rectangle(
            [x_pos, screen_y, x_pos + button_width, screen_y + button_height],
            fill=bg_color
        )

        # Draw text
        text_color = (0, 0, 0) if selected else (255, 255, 255)
        for y, row in enumerate(label_matrix):
            for x, pixel in enumerate(row):
                if pixel != (0, 0, 0):
                    self.draw.rectangle(
                        [x_pos + x, screen_y + y, x_pos + x , screen_y + y],
                        fill=text_color
                    )

    def start_end_animation(self, mode, cause=None, sprite_folder=None):
        self.end_mode = mode
        self.end_start_time = time.time()
        self.death_cause = cause
        self.death_sprite_folder = sprite_folder

    def draw_end_animation(self):
        elapsed = time.time() - self.end_start_time
        if self.end_mode == 'win':
            self.play_win_animation()
        elif self.end_mode == 'lose':
            self.play_lose_animation(self.death_cause, self.death_sprite_folder)


    def play_win_animation(self):
        if self.end_start_time is None:
            self.end_start_time = time.time()
        elapsed = time.time() - self.end_start_time
        if int(elapsed * 5) % 2 == 0:  # Flash every ~0.2s
            flash_color = random.choice([
                (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                (255, 0, 255), (0, 255, 255)
            ])
            self.draw.rectangle([0, 0, self.matrix_width, self.matrix_height], fill=flash_color)

        self.draw_text_centered("YOU HAVE ASCENDED")


    def play_lose_animation(self, cause, sprite_folder):
        if self.end_start_time is None:
            self.end_start_time = time.time()
            self.death_cause = cause
            self.death_sprite_folder = sprite_folder

        elapsed = time.time() - self.end_start_time

        if elapsed > 6:
            self.in_death_animation = False
            return  # Stop drawing, exit animation

        sprite_path = f"{self.death_sprite_folder}/sprite0.png"

        match self.death_cause:
            case 'food':
                self.draw_death_hunger(elapsed, sprite_path)
            case 'rest':
                self.draw_death_rest(elapsed, sprite_path)
            case 'social':
                self.draw_death_social(elapsed, sprite_path)
            case 'safe':
                self.draw_death_safe(elapsed, sprite_path)
            case 'esteem':
                self.draw_death_esteem(elapsed, sprite_path)

    def draw_death_hunger(self, elapsed, sprite_path):
        scale = max(0.01, 1 - elapsed * 0.6)
        self.draw_sprite_at(25, 10, sprite_path, sprite_width=max(1, int(14 * scale)), sprite_height=14)
        if scale <= 0.02:
            self.clear_screen()
            self.draw_text_centered("YOU STARVED")

    def draw_death_rest(self, elapsed, sprite_path):
        scale = max(0.01, 1 - elapsed * 0.6)
        self.draw_sprite_at(25, 10 + scale, sprite_path, sprite_width=14, sprite_height=max(1, int(14 * scale)))
        if scale <= 0.02:
            self.clear_screen()
            self.draw_text_centered("YOU CAN SLEEP NOW")

    def draw_death_social(self, elapsed, sprite_path):
        for i in range(3):
            x_offset = int(elapsed * (i + 1) * 3)
            self.draw_sprite_at(10 + i * 15 + x_offset, 10, f"assets/sprites/otherTama/tama{i}.png")
        if elapsed > 5:
            self.clear_screen()
            self.draw_text_centered("YOU DIED ALONE")

    def draw_death_safe(self, elapsed, sprite_path):
        self.draw_sprite_at(30, 10, sprite_path)
        if elapsed > 1:
            self.draw_sprite_at(34, 10, "assets/sprites/fx/gun.png")
        if elapsed > 1:
            self.draw_sprite_at(50, 10, "assets/sprites/fx/bullet_hit.png")
        if elapsed > 3:
            self.clear_screen()
            self.draw_text_centered("YOU DIED")

    def draw_death_esteem(self, elapsed, sprite_path):
        self.draw_sprite_at(30, 10, sprite_path)
        if elapsed > 1:
            self.draw_sprite_at(39, 10, "assets/sprites/fx/gun.png")
        if elapsed > 2:
            self.draw_sprite_at(34, 10, "assets/sprites/fx/bullet_hit.png")
        if elapsed > 3:
            self.clear_screen()
            self.draw_text_centered("YOU KILLED YOUSELF")

    def end_animation_done(self):
        return time.time() - self.end_start_time > 6



    def clear_screen(self):
        """Clear the screen by filling it with black."""
        self.draw.rectangle([0, 0, self.canvas.width, self.canvas.height], fill=self.black)
