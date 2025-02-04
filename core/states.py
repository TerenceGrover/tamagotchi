class States:
    def __init__(self):
        self.current_screen = "home_screen"  # Default screen
        self.stage_of_life = "adult"          # Default stage
        self.character = "whore1"          # Default character

    def transition_to_screen(self, new_screen):
        print(f"Transitioning from {self.current_screen} to {new_screen}")
        self.current_screen = new_screen

    def transition_to_life_stage(self, new_stage):
        print(f"Transitioning from {self.stage_of_life} to {new_stage}")
        self.stage_of_life = new_stage

    def get_sprite_folder(self):
        """
        Get the sprite folder path based on the current life stage and character.

        Returns:
            str: Path to the sprite folder.
        """
        return f"assets/"
