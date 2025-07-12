import time
from core.minigames.platformer import initialize_platformer
from core.minigames.hobby import initialize_hobby  # Import Hobby Minigame
from core.minigames.job import initialize_job  # Placeholder for Job Minigame

RANDOM_EVENTS = [
    {
        "prompt": "try crack?",
        "yes": lambda stats: (
            stats.modify_stat("esteem", 999),
            stats.modify_stat("safe", -stats.stats["safe"] // 2)
        ),
        "no": lambda stats: None
    },
    {
        "prompt": "commit tax fraud?",
        "yes": lambda stats: (
            stats.modify_stat("money", 20),
            stats.modify_stat("safe", -30),
        ),
        "no": lambda stats: stats.modify_stat("safe", 5)
    },
    {
        "prompt": "date a teen?",
        "yes": lambda stats: (
            stats.modify_stat("esteem", 20),
            stats.modify_stat("safe", -stats.stats["safe"])
        ),
        "no": lambda stats: None
    },
    {
        "prompt": "become religious?",
        "yes": lambda stats: (
            stats.modify_stat("safe", 10),
            stats.modify_stat("social", -10)
        ),
        "no": lambda stats: stats.modify_stat("esteem", 10)
    },
    {
    "prompt": "join a cult?",
    "yes": lambda stats: (
        stats.modify_stat("social", 20),
        stats.modify_stat("esteem", -10),
        stats.modify_stat("safe", -stats.stats["safe"] // 2)
    ),
    "no": lambda stats: stats.modify_stat("esteem", 5)
    },
    {
        "prompt": "sell a kidney?",
        "yes": lambda stats: (
            stats.modify_stat("money", 50),
            stats.modify_stat("safe", -20)
        ),
        "no": lambda stats: stats.modify_stat("esteem", -5)
    },
    {
        "prompt": "buy gun?",
        "yes": lambda stats: (
            stats.modify_stat("safe", 30),
            stats.modify_stat("social", -15)
        ),
        "no": lambda stats: stats.modify_stat("safe", -5)
    },
    {
        "prompt": "incite a riot?",
        "yes": lambda stats: (
            stats.modify_stat("esteem", 20),
            stats.modify_stat("social", 20),
            stats.modify_stat("safe", -10)
        ),
        "no": lambda stats: stats.modify_stat("social", -10)
    },
    {
        "prompt": "drink bleach?",
        "yes": lambda stats: (
            stats.modify_stat("safe", -100),
            stats.modify_stat("esteem", 999)  # go out proud
        ),
        "no": lambda stats: stats.modify_stat("safe", 5)
    }
]

class States:
    def __init__(self):
        self.stage_of_life = "egg"  # Default stage
        self.character = "whore1"  # Default character
        self.current_screen = "home_screen"  # Default screen
        self.social_state = None  # Socializing game state
        self.selected_point_index = 0  # Default point selection
        self.animation_frame = None
        self.selected_level = None
        self.animation_start_time = None
        self.student_loan = 0
        self.housing_state = None
        self.education_options = [
            {"level": "HS", "loan": 5000},
            {"level": "BSc", "loan": 20000},
            {"level": "MSc", "loan": 50000},
            {"level": "PhD", "loan": 100000}
        ]
        self.platformer_state = None  # Holds platformer game state
        self.hobby_state = None  # Holds hobby game state
        self.hobby_high_score = 0  # High score for hobby minigame
        self.job_state = None  # Holds job game state (to be implemented)
        self.random_event = {
            "active": False,
            "prompt": "",
            "outcome": None,
            "cooldown_timer": time.time(),
            "selection": "yes"  # or "no"
        }

        self.point_screens = [
            "education_screen", "hobby_screen", "food_screen",  
            "socialize_screen", "job_screen", "housing_screen"
        ]

        self.all_screens = {
            "egg": ["stats_screen"],
            "small": ["stats_screen", "education_screen" if self.selected_level is None else None, "food_screen", "socialize_screen", "hobby_screen"],
            "adult": ["stats_screen", "education_screen", "food_screen", "socialize_screen", "hobby_screen", "job_screen", "housing_screen"],
            "dead": ["end_screen"]
        }

        # Age-related properties
        self.age = 0
        self.start_time = time.time()
        self.life_stages = {"egg": 0, "small":0 , "adult": 350000, "dead" : 100000000}  # Age thresholds

    def update_life_stage(self):
        """
        Update the life stage based on the elapsed time.
        """
        elapsed_time = time.time() - self.start_time
        if self.stage_of_life == "egg" and elapsed_time > self.life_stages["egg"]:
            self.transition_to_life_stage("small")
        elif self.stage_of_life == "small" and elapsed_time > self.life_stages["small"]:
            self.transition_to_life_stage("adult")
        elif self.stage_of_life == "adult" and elapsed_time > self.life_stages["adult"]:
            self.transition_to_life_stage("dead")

    def update_education(self, level, loan):
        """
        Update education level and associated student loan.
        """
        self.education_level = level
        self.student_loan = loan
        print(f"Education Level: {level}, Student Loan: ${loan}")

    def transition_to_life_stage(self, new_stage):
        """
        Transition to a new life stage.
        """
        print(f"Transitioning from {self.stage_of_life} to {new_stage}")
        self.stage_of_life = new_stage
        self.start_time = time.time()  # Reset timer for the new stage

    def transition_to_screen(self, new_screen):
        """
        Transition to a new screen.
        """
        print(f"Transitioning to {new_screen}")
        self.current_screen = new_screen

    def cycle_point(self):
        """
        Cycle through the points on the home screen.
        """
        self.selected_point_index = (self.selected_point_index + 1) % len(self.point_screens)

    def get_current_screen_from_point(self):
        """
        Get the screen associated with the currently selected point.
        """
        return self.point_screens[self.selected_point_index]
    
    def get_sprite_folder(self):
        """
        Get the sprite folder path based on the current life stage and character.
        """
        return f"assets/sprites/{self.character}/{self.stage_of_life}"
    
    def start_platformer(self, money_stats):
        """
        Initialize the platformer minigame state.
        """
        self.platformer_state = initialize_platformer(money_stats)

    def reset_platformer(self):
        """
        Reset the platformer minigame.
        """
        self.platformer_state = None

    def start_hobby(self):
        """
        Initialize the hobby rhythm-based minigame.
        """
        self.hobby_state = initialize_hobby(self)

    def reset_hobby(self):
        """
        Reset the hobby minigame.
        """
        self.hobby_state = None

    def update_hobby_high_score(self, score):
        """
        Update the high score for the hobby minigame.
        """
        if score > self.hobby_high_score:
            self.hobby_high_score = score
            print(f"New Hobby High Score: {self.hobby_high_score}")

    def start_job(self):
        """
        Initialize the job mini-game (to be implemented).
        """
        if self.stage_of_life == "adult":
            self.job_state = initialize_job()

    def reset_job(self):
        """
        Reset the job mini-game (to be implemented).
        """
        self.job_state = None

    def get_available_screens(self):
        """
        Get the list of available screens based on the life stage.
        """
        return self.all_screens[self.stage_of_life]

    def is_screen_available(self, screen_name):
        """
        Check if a screen is available based on the current life stage.
        """
        return screen_name in self.get_available_screens()
