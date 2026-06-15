# Quests Of The Shadowland

A 2D side-scrolling action platformer built with Python and Pygame. Fight through 10 levels of soldiers, enemies, and zombies — collect coins, grab loot boxes, and survive to reach the highest score.

---

## Features

- 10 hand-crafted levels with scrolling tile-based worlds
- Three enemy types: Soldiers, Enemies, and Zombies (with melee bite attacks)
- Combat with bullets and grenades, including explosion animations
- Loot boxes: Med-kit, Ammo-kit, and Grenade-kit
- Collectible coins (10 points each)
- Persistent high score and level progress saved between sessions (encrypted via Fernet)
- Animated sprites for player and enemies: Idle, Run, Jump, Death
- Water hazards with splash effects
- Background parallax scrolling
- Full audio: background music, jump, landing, shooting, explosion, coin collect, game over, level up, and click SFX
- Built-in **Level Editor** for creating and modifying levels

---

## Requirements

- Python 3.8+
- [pygame](https://www.pygame.org/)
- [python-decouple](https://pypi.org/project/python-decouple/)
- [fernet](https://pypi.org/project/fernet/)

Install dependencies:

```bash
pip install pygame python-decouple fernet
```

---

## Project Structure

```
Quests_Of_The_Shadowland/
├── main.py              # Main game loop and all game classes
├── LevelEditor.py       # Standalone level editor tool
├── Button.py            # Reusable UI button component
├── cryptographer.py     # Fernet-based save data encryption/decryption
├── .env                 # Encrypted game state (level, max level, high score)
├── audio/               # Sound effects and background music
│   ├── background_music.mp3
│   ├── click.mp3
│   ├── coin_collect.mp3
│   ├── explosion.mp3
│   ├── game_over.mp3
│   ├── jump.mp3
│   ├── landing.mp3
│   ├── level_up.mp3
│   ├── shot.mp3
│   └── water_splash.mp3
├── img/
│   ├── Background/      # Parallax background layers (0–11)
│   ├── Buttons/         # UI button images
│   ├── Characters/
│   │   ├── Player/      # Player animations (Idle, Run, Jump, Death)
│   │   ├── Enemy/       # Enemy animations
│   │   └── Zombie/      # Zombie animations
│   ├── Coin/            # Animated coin frames
│   ├── Door/            # Level exit gateway
│   ├── Explosion/       # Grenade explosion frames
│   ├── Icons/           # HUD icons (bullet, grenade, ammo, med-kit)
│   ├── Logo/            # Title card and window icon
│   ├── Tile/            # World tiles (23 types)
│   └── Water/           # Animated water hazard frames
└── world_data/          # Serialised level data (levels 1–10 + 14)
```

---

## How to Run

```bash
python main.py
```

The game window opens at **800 × 640** pixels at 60 FPS.

---

## Controls

| Key | Action |
|-----|--------|
| `A` | Move left |
| `D` | Move right |
| `W` | Jump |
| `Space` | Shoot |
| `E` | Throw grenade |
| `Escape` | Quit |

---

## Game Mechanics

**Player** starts with 100 HP, a starting ammo count, and grenades. Health, ammo, and grenades can be replenished by collecting loot boxes scattered across each level.

**Enemies and Zombies** use a vision cone to detect the player. Soldiers shoot bullets; Zombies without ammo will chase and bite the player (dealing 20 damage per bite).

**Coins** are worth 10 points each. Your score accumulates across a run and is compared to the stored high score at game over.

**Level completion** is triggered by reaching the door/gateway at the end of the level. Falling into water kills the player instantly.

**Save data** (current level, max level reached, high score) is stored encrypted in `.env` using Fernet symmetric encryption.

---

## Level Editor

A separate tool for building and editing levels is included:

```bash
python LevelEditor.py
```

The editor operates on the same tile set and world data format used by the main game. Levels are saved as pickled data files in the `world_data/` directory.

---

## Save System

Progress is stored in `.env` as Fernet-encrypted, base64-encoded values for three keys:

- `LEVEL` — the player's current level
- `MAX_LEVEL` — the highest level unlocked (default: 10)
- `HIGH_SCORE` — the all-time high score

The encryption key lives in `cryptographer.py`. Running `cryptographer.py` directly resets all save data to defaults (Level 1, Max Level 10, High Score 0).

---

## License

This project does not include a license file. All rights reserved by the author unless stated otherwise.