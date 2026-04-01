# 🐣 Homie MCP

A tamagotchi-style virtual pet for your coding sessions. Hatch a unique homie, pet it, and watch it react to your work.

Each homie is deterministically generated from a seed string, so yours is always the same across machines.

## What it looks like

```
   ♛
  \v/ \v/
  (✦ ~ ✦)
  <~~~~~>
   vvvvv

╔════════════════════════════════════╗
║              Sparky                ║
║              DRAGON                ║
║         ★★★★ Epic                  ║
╠════════════════════════════════════╣
║ DEBUGGING  ████████░░░░░░░  55    ║
║ PATIENCE   ██████░░░░░░░░░  40    ║
║ CHAOS      █████████████░░  88    ║
║ WISDOM     ███████░░░░░░░░  47    ║
║ SNARK      ██████████░░░░░  68    ║
╚════════════════════════════════════╝
```

## 18 species

duck, goose, blob, cat, dragon, octopus, owl, penguin, turtle, snail, ghost, axolotl, capybara, cactus, robot, rabbit, mushroom, chonk

5 rarity tiers (Common through Legendary), shiny variants (1% chance), hat accessories for uncommon+, and 5 RPG stats: DEBUGGING, PATIENCE, CHAOS, WISDOM, SNARK.

## Setup

Requires Python 3.10+

```bash
git clone https://github.com/kilo-loco/mcp-buddy.git
cd mcp-buddy
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Verify it works

```bash
python3 server.py
```

You should see the server start with no errors. Press `Ctrl+C` to stop it.

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "homie": {
      "command": "/path/to/mcp-buddy/.venv/bin/python3",
      "args": ["/path/to/mcp-buddy/server.py"]
    }
  }
}
```

Replace `/path/to/mcp-buddy` with the actual path where you cloned the repo.

### Claude Code

```bash
claude mcp add homie /path/to/mcp-buddy/.venv/bin/python3 /path/to/mcp-buddy/server.py
```

Replace `/path/to/mcp-buddy` with the actual path where you cloned the repo.

## Tools

| Tool | What it does |
|------|-------------|
| `hatch_homie` | Generate a new homie from a name and optional seed. Returns species, rarity, stats, ASCII sprite, personality. |
| `get_homie` | Show your current homie's sprite, stats, and personality. |
| `pet_homie` | Pet your homie. Hearts animation, species-specific reaction, interaction counter. |
| `homie_react` | Give context about your work ("debugging a memory leak") and your homie reacts in character. |
| `homie_stats` | Full RPG stat card with visual bars. |
| `rename_homie` | Change your homie's name. |

### Example

> "Hatch me a homie named Sparky"

```
🥚 *crack* ... *crack crack* ...

  \v/ \v/
  (✦ ~ ✦)
  <~~~~~>
   vvvvv

🎉 Sparky has hatched!
Species: Dragon
Rarity: ★★★★ Epic
Personality: Dramatic flair. Breathes fire at bugs. Hoards good code snippets.
```

> "Tell my homie I'm debugging a memory leak"

```
  \v/ \v/
  (✦ ~ ✦)
  <~~~~~>
   vvvvv

💬 *dragon adjusts tiny glasses* Have you tried reading the error message?
```

## How it works

Companions are deterministically generated from a seed string via SHA-256. Same seed, same homie, every time. State (name, hatch date, interaction count) is stored in `~/.homie-mcp/homie.json`.

### Rarity distribution

| Rarity | Chance | Stat floor | Hats? |
|--------|--------|------------|-------|
| Common ★ | 60% | 5 | No |
| Uncommon ★★ | 25% | 15 | Yes |
| Rare ★★★ | 10% | 25 | Yes |
| Epic ★★★★ | 4% | 35 | Yes |
| Legendary ★★★★★ | 1% | 50 | Yes |

Each homie gets one peak stat and one dump stat, so no two feel the same.

## License

MIT
