
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window

Window.clearcolor = (0.055, 0.075, 0.13, 1)

BG = (0.055, 0.075, 0.13, 1)
CARD = (0.12, 0.16, 0.26, 1)
BLUE = (0.27, 0.42, 0.85, 1)
GREEN = (0.18, 0.62, 0.42, 1)


def make_button(text, callback, color=BLUE):
    b = Button(
        text=text,
        font_size=dp(17),
        background_normal="",
        background_color=color,
        color=(1, 1, 1, 1),
        size_hint_y=None,
        height=dp(52)
    )
    b.bind(on_release=callback)
    return b


def make_label(text, size=22):
    return Label(
        text=text,
        font_size=dp(size),
        color=(1, 1, 1, 1),
        size_hint_y=None,
        height=dp(48)
    )


# -------------------------
# MAIN HUB
# -------------------------

class Hub(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(14)
        )

        layout.add_widget(make_label("🎮 ARCADE WORLD", 30))
        layout.add_widget(make_label("Choose your game!", 19))

        layout.add_widget(make_button(
            "💣  MINESWEEPER",
            lambda x: self.open_game("mines")
        ))

        layout.add_widget(make_button(
            "🐍  SNAKE",
            lambda x: self.open_game("snake"),
            GREEN
        ))

        layout.add_widget(make_button(
            "🍄  GARDEN GNOMES",
            lambda x: self.open_game("garden"),
            (0.48, 0.30, 0.65, 1)
        ))

        layout.add_widget(make_label("More games coming soon!", 14))

        self.add_widget(layout)

    def open_game(self, game):
        app = App.get_running_app()
        app.start_game(game)


# -------------------------
# GAME BASE
# -------------------------

class GameScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(7)
        )

        self.add_widget(self.layout)

        self.layout.add_widget(make_button(
            "← BACK TO HUB",
            lambda x: self.back(),
            CARD
        ))

        self.status = make_label("Let's play!", 18)
        self.layout.add_widget(self.status)

    def back(self):
        Clock.unschedule(self.update_snake)
        App.get_running_app().manager.current = "hub"


# -------------------------
# MINESWEEPER
# -------------------------

class Minesweeper(GameScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size = 8
        self.mine_count = 10
        self.flag_mode = False

        self.layout.add_widget(make_button(
            "🚩 TOGGLE FLAG MODE",
            lambda x: self.toggle_flag(),
            (0.65, 0.35, 0.25, 1)
        ))

        self.board = GridLayout(
            cols=self.size,
            spacing=dp(2),
            size_hint_y=1
        )

        self.layout.add_widget(self.board)
        self.new_game()

    def new_game(self):
        self.mines = set(
            random.sample(range(64), self.mine_count)
        )
        self.opened = set()
        self.flags = set()
        self.over = False
        self.flag_mode = False

        self.buttons = []

        self.board.clear_widgets()

        for i in range(64):
            b = Button(
                text="",
                font_size=dp(16),
                background_normal="",
                background_color=(0.22, 0.29, 0.43, 1)
            )
            b.bind(
                on_release=lambda btn, n=i: self.tap(n)
            )
            self.buttons.append(b)
            self.board.add_widget(b)

        self.status.text = "Find all 10 mines!"

    def toggle_flag(self):
        self.flag_mode = not self.flag_mode
        self.status.text = (
            "🚩 Flag mode ON" if self.flag_mode
            else "Open mode ON"
        )

    def neighbors(self, n):
        r, c = divmod(n, 8)
        result = []

        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    result.append(nr * 8 + nc)

        return result

    def tap(self, n):
        if self.over or n in self.opened:
            return

        if self.flag_mode:
            if n in self.flags:
                self.flags.remove(n)
                self.buttons[n].text = ""
            else:
                self.flags.add(n)
                self.buttons[n].text = "🚩"
            return

        if n in self.flags:
            return

        if n in self.mines:
            self.over = True
            self.buttons[n].text = "💣"

            for mine in self.mines:
                self.buttons[mine].text = "💣"

            self.status.text = "Game over! Try again."
            self.layout.add_widget(make_button(
                "RESTART",
                lambda x: self.restart()
            ))
            return

        self.reveal(n)

        if len(self.opened) == 64 - self.mine_count:
            self.over = True
            self.status.text = "🎉 You won!"
            self.layout.add_widget(make_button(
                "PLAY AGAIN",
                lambda x: self.restart()
            ))

    def reveal(self, n):
        if n in self.opened or n in self.mines:
            return

        self.opened.add(n)

        count = sum(
            x in self.mines for x in self.neighbors(n)
        )

        b = self.buttons[n]
        b.text = str(count) if count else ""
        b.background_color = (0.38, 0.43, 0.54, 1)

        if count == 0:
            for neighbor in self.neighbors(n):
                if neighbor not in self.opened:
                    self.reveal(neighbor)

    def restart(self):
        self.layout.clear_widgets()
        self.layout.add_widget(make_button(
            "← BACK TO HUB", lambda x: self.back(), CARD
        ))
        self.status = make_label("Find all 10 mines!", 18)
        self.layout.add_widget(self.status)
        self.layout.add_widget(make_button(
            "🚩 TOGGLE FLAG MODE",
            lambda x: self.toggle_flag(),
            (0.65, 0.35, 0.25, 1)
        ))
        self.board = GridLayout(cols=8, spacing=dp(2))
        self.layout.add_widget(self.board)
        self.new_game()


# -------------------------
# SNAKE
# -------------------------

class Snake(GameScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout.add_widget(make_label("🐍 SNAKE", 25))

        self.board = GridLayout(
            cols=12,
            spacing=dp(2),
            size_hint_y=1
        )
        self.layout.add_widget(self.board)

        controls = GridLayout(
            cols=3,
            size_hint_y=None,
            height=dp(155),
            spacing=dp(5)
        )

        controls.add_widget(Label())
        controls.add_widget(make_button(
            "⬆️", lambda x: self.change_dir((0, 1))
        ))
        controls.add_widget(Label())

        controls.add_widget(make_button(
            "⬅️", lambda x: self.change_dir((-1, 0))
        ))
        controls.add_widget(make_button(
            "⬇️", lambda x: self.change_dir((0, -1))
        ))
        controls.add_widget(make_button(
            "➡️", lambda x: self.change_dir((1, 0))
        ))

        self.layout.add_widget(controls)

        self.new_game()

    def new_game(self):
        Clock.unschedule(self.update_snake)

        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)
        self.food = (random.randint(0, 11),
                     random.randint(0, 11))
        self.score = 0
        self.over = False

        self.refresh()
        Clock.schedule_interval(self.update_snake, 0.23)

    def change_dir(self, d):
        if (d[0] + self.direction[0] == 0 and
                d[1] + self.direction[1] == 0):
            return

        self.direction = d

    def update_snake(self, dt):
        if self.over:
            return

        x, y = self.snake[0]
        dx, dy = self.direction
        head = (x + dx, y + dy)

        if (not 0 <= head[0] < 12 or
                not 0 <= head[1] < 12 or
                head in self.snake[:-1]):
            self.over = True
            Clock.unschedule(self.update_snake)
            self.status.text = (
                "Game over! Score: " + str(self.score)
            )
            self.layout.add_widget(make_button(
                "PLAY AGAIN",
                lambda b: self.restart()
            ))
            return

        self.snake.insert(0, head)

        if head == self.food:
            self.score += 1
            self.food = (
                random.randint(0, 11),
                random.randint(0, 11)
            )
        else:
            self.snake.pop()

        self.status.text = "Score: " + str(self.score)
        self.refresh()

    def refresh(self):
        self.board.clear_widgets()

        for y in reversed(range(12)):
            for x in range(12):
                pos = (x, y)

                if pos == self.snake[0]:
                    color = (0.2, 0.9, 0.45, 1)
                    txt = "●"
                elif pos in self.snake:
                    color = (0.1, 0.55, 0.3, 1)
                    txt = "●"
                elif pos == self.food:
                    color = (0.95, 0.25, 0.25, 1)
                    txt = "🍎"
                else:
                    color = (0.13, 0.19, 0.28, 1)
                    txt = ""

                b = Button(
                    text=txt,
                    background_normal="",
                    background_color=color,
                    font_size=dp(12)
                )
                self.board.add_widget(b)

    def restart(self):
        self.layout.clear_widgets()
        self.layout.add_widget(make_button(
            "← BACK TO HUB", lambda x: self.back(), CARD
        ))
        self.status = make_label("Score: 0", 18)
        self.layout.add_widget(self.status)
        self.board = GridLayout(cols=12, spacing=dp(2))
        self.layout.add_widget(self.board)
        self.new_game()

        controls = GridLayout(
            cols=3,
            size_hint_y=None,
            height=dp(155),
            spacing=dp(5)
        )

        controls.add_widget(Label())
        controls.add_widget(make_button(
            "⬆️", lambda x: self.change_dir((0, 1))
        ))
        controls.add_widget(Label())
        controls.add_widget(make_button(
            "⬅️", lambda x: self.change_dir((-1, 0))
        ))
        controls.add_widget(make_button(
            "⬇️", lambda x: self.change_dir((0, -1))
        ))
        controls.add_widget(make_button(
            "➡️", lambda x: self.change_dir((1, 0))
        ))

        self.layout.add_widget(controls)


# -------------------------
# GARDEN GNOMES
# -------------------------

class Garden(GameScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout.add_widget(make_label(
            "🍄 GARDEN GNOMES", 24
        ))

        self.layout.add_widget(make_label(
            "Find the hidden garden gnomes!", 15
        ))

        self.board = GridLayout(
            cols=5,
            spacing=dp(5),
            size_hint_y=1
        )

        self.layout.add_widget(self.board)

        self.new_game()

    def new_game(self):
        self.gnomes = set(random.sample(range(25), 5))
        self.weeds = set(
            random.sample(
                list(set(range(25)) - self.gnomes), 5
            )
        )

        self.clicked = set()
        self.score = 0
        self.over = False
        self.buttons = []

        self.board.clear_widgets()

        for i in range(25):
            b = Button(
                text="🌿",
                font_size=dp(24),
                background_normal="",
                background_color=(0.16, 0.43, 0.28, 1)
            )
            b.bind(
                on_release=lambda btn, n=i: self.tap(n)
            )
            self.buttons.append(b)
            self.board.add_widget(b)

        self.status.text = "Gnomes found: 0 / 5"

    def tap(self, n):
        if self.over or n in self.clicked:
            return

        self.clicked.add(n)
        b = self.buttons[n]

        if n in self.gnomes:
            b.text = "🧙"
            b.background_color = GREEN
            self.score += 1
            self.status.text = (
                "Gnomes found: " + str(self.score) + " / 5"
            )

        elif n in self.weeds:
            b.text = "🥀"
            b.background_color = (0.5, 0.25, 0.22, 1)

        else:
            b.text = "🌸"
            b.background_color = (0.28, 0.43, 0.30, 1)

        if self.score == 5:
            self.over = True
            self.status.text = "🎉 All gnomes found!"
            self.layout.add_widget(make_button(
                "NEW GARDEN",
                lambda x: self.restart()
            ))

        elif len(self.clicked) == 25:
            self.over = True
            self.status.text = "Garden explored!"
            self.layout.add_widget(make_button(
                "TRY AGAIN",
                lambda x: self.restart()
            ))

    def restart(self):
        self.layout.clear_widgets()
        self.layout.add_widget(make_button(
            "← BACK TO HUB", lambda x: self.back(), CARD
        ))
        self.layout.add_widget(make_label(
            "🍄 GARDEN GNOMES", 24
        ))
        self.layout.add_widget(make_label(
            "Find the hidden garden gnomes!", 15
        ))
        self.status = make_label("Gnomes found: 0 / 5", 18)
        self.layout.add_widget(self.status)
        self.board = GridLayout(cols=5, spacing=dp(5))
        self.layout.add_widget(self.board)
        self.new_game()


# -------------------------
# APP
# -------------------------

class ArcadeApp(App):

    def build(self):
        self.manager = ScreenManager()
        self.manager.add_widget(Hub(name="hub"))
        self.manager.current = "hub"
        return self.manager

    def start_game(self, game):
        if game == "mines":
            screen = Minesweeper(name="game")
        elif game == "snake":
            screen = Snake(name="game")
        elif game == "garden":
            screen = Garden(name="game")

        if self.manager.has_screen("game"):
            old = self.manager.get_screen("game")
            if hasattr(old, "back"):
                Clock.unschedule(old.update_snake) if isinstance(
                    old, Snake
                ) else None
            self.manager.remove_widget(old)

        self.manager.add_widget(screen)
        self.manager.current = "game"


if __name__ == "__main__":
    ArcadeApp().run()

