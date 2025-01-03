import time

class States:
    def __init__(self):
        self.current_screen = "home_screen"  # Default screen
        self.stage_of_life = "egg"          # Start as an egg
        self.character = "whore1"          # Default character
        self.start_time = time.time()      # Track game start time
        self.life_stages = {
            "egg": 15,     # Time in seconds to transition to 'small'
            "small": 30,   # Time to transition to 'adult'
            "adult": 60,   # Time to transition to 'dead'
        }

    def transition_to_screen(self, new_screen):
        print(f"Transitioning from {self.current_screen} to {new_screen}")
        self.current_screen = new_screen

    def update_life_stage(self):
        """
        Update the life stage based on elapsed time.
        """
        elapsed_time = time.time() - self.start_time

        if self.stage_of_life == "egg" and elapsed_time > self.life_stages["egg"]:
            self.transition_to_life_stage("small")
        elif self.stage_of_life == "small" and elapsed_time > self.life_stages["small"]:
            self.transition_to_life_stage("adult")
        elif self.stage_of_life == "adult" and elapsed_time > self.life_stages["adult"]:
            self.transition_to_life_stage("dead")

    def transition_to_life_stage(self, new_stage):
        print(f"Transitioning from {self.stage_of_life} to {new_stage}")
        self.stage_of_life = new_stage

    def get_sprite_folder(self):
        """
        Get the sprite folder path based on the current life stage and character.

        Returns:
            str: Path to the sprite folder.
        """
        return f"assets/sprites/{self.character}/{self.stage_of_life}"
