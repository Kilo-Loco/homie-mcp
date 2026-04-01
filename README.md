# 🐣 MCP Buddy

A tamagotchi-style virtual companion pet for your coding sessions. Inspired by virtual pets and the joy of having a little buddy watch you code.

Hatch a unique companion, pet it, and watch it react to your work. Each companion is deterministically generated from a seed, so your buddy is uniquely yours.

## Features

- **18 species** including duck, dragon, ghost, axolotl, capybara, and more
- **5 rarity tiers**: Common ★, Uncommon ★★, Rare ★★★, Epic ★★★★, Legendary ★★★★★
- **Shiny variants** (1% chance) with sparkle effects
- **RPG stat system**: DEBUGGING, PATIENCE, CHAOS, WISDOM, SNARK
- **Personality-driven reactions** based on species and stats
- **ASCII art sprites** with hat accessories
- **Persistent state** saved between sessions

## Species Gallery

```
  Duck           Cat            Dragon         Ghost          Robot
   _~           ^   ^         \v/ \v/         .---.         [====]
 (·  )>        (· w ·)        (· ~ ·)       | ·  ·|       | ·  · |
 /|__|          )   (         <~~~~~>       |  o  |       |_====_|
  ^ ^          ~~ _ ~~         vvvvv        ~^~^~^~        d|  |b

  Axolotl       Capybara       Mushroom       Chonk         Octopus
\~(    )~/     .______.      .~o~~O~~.       _/\ /\_       .~~~~~~.
\~(·  ·)~/    (·      ·)    (________)     / ·    · \    ( ·    · )
  (~~~~)      (  oooo  )      |·  ·|      (   ....   )   (______)
  d/  \b       `------'       |____|       \_______/     ~/~/~/~/~
```

## Installation

```bash
# Clone the repo
git clone https://github.com/kilo-loco/mcp-buddy.git
cd mcp-buddy

# Install dependencies
pip install -r requirements.txt
```

## Usage with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "buddy": {
      "command": "python",
      "args": ["/path/to/mcp-buddy/server.py"]
    }
  }
}
```

## Usage with Claude Code

Add to your Claude Code MCP config:

```bash
claude mcp add buddy python /path/to/mcp-buddy/server.py
```

## MCP Tools

### `hatch_companion`
Generate a new companion from a name and optional seed.
- **name** (required): What to name your companion
- **seed** (optional): Seed string for deterministic generation (defaults to name)
- Returns: Species, rarity, stats, ASCII art, personality

### `get_companion`
Get your current companion's info and ASCII art sprite.

### `pet_companion`
Pet your companion! Returns hearts animation and a cute species-specific reaction. Tracks interaction count.

### `companion_react`
Give context about what you're working on and your companion reacts in character.
- **context** (required): What you're doing (e.g., "debugging a memory leak")
- Reactions are influenced by personality, species, and stat distribution

### `companion_stats`
Show a full RPG-style stat card with visual bars.

### `rename_companion`
Give your companion a new name.
- **new_name** (required): The new name

## How It Works

Companions are deterministically generated from a seed string using SHA-256 hashing. The same seed always produces the same species, rarity, stats, and appearance. Your companion's "soul" (name, hatch date, interaction count) is stored in `~/.mcp-buddy/companion.json`.

### Rarity Distribution
| Rarity | Chance | Stat Floor | Hat? |
|--------|--------|------------|------|
| Common ★ | 60% | 5 | No |
| Uncommon ★★ | 25% | 15 | Yes |
| Rare ★★★ | 10% | 25 | Yes |
| Epic ★★★★ | 4% | 35 | Yes |
| Legendary ★★★★★ | 1% | 50 | Yes |

### Stats
Each companion has 5 stats (1-100) that influence their personality:
- **DEBUGGING**: Bug-finding instinct
- **PATIENCE**: How calmly they handle problems
- **CHAOS**: Tendency toward creative destruction
- **WISDOM**: Deep knowledge and insight
- **SNARK**: Sass levels (may roast your code)

Higher rarity companions have higher stat floors. Each companion has one peak stat and one dump stat, making every buddy unique.

## License

MIT
