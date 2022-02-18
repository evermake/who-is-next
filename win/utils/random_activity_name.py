from random import choice

CHOICES = (
    "Repair toilets 👨‍🎓",
    "Чистить говно 💩",
    "Варить носки 🧦",
    "Заниматься разработкой атомной бомбы 'КУПАТА-JESSy' 💣",
)


def get_random_activity_name() -> str:
    return choice(CHOICES)
