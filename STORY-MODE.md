# STORY MODE — what is actually in the build

Companion to [SEVEN-LANTERNS-story-bible-EN.md](SEVEN-LANTERNS-story-bible-EN.md).
The bible is the intent; this is the shipped shape, and where the two differ
this file wins.

Everything lives in `index.html`. The relevant sections are `6C. THE STORY`
(cast, chapters, dialogue), `2B. WARDENS` (the three story bosses), and
`WARDEN FIGHTS` inside `class Game`.

---

## 1. The road

The splash Play button is the story. Free play, endless and the run board are
secondary buttons beside it.

A **chapter** is one authored map plus the scene that opens it, the barks that
play over it, and the scene that closes it. Thirteen chapters, index-aligned to
`STAGE_CONFIGS` — chapter N is map N. A load-time check warns if that stops
being true.

**Progress is by reaching the gate, not by score.** Par still exists and still
gates free play, but in the story it is only a mastery seal — nobody is stopped
from finding out what happens next. Clearing a chapter also unlocks the
matching free-play map, so a player who only ever presses Play still ends up
with the whole grid open.

| # | Kanji | Chapter | Wall at the end |
|---|-------|---------|-----------------|
| 01 | 歩 | The First Step | — |
| 02 | 竹 | The Bamboo Path | — |
| 03 | 霧 | The Mist Ravine | — |
| 04 | 城 | The Fortress Gates | TETSU-DOKURO (hovering) |
| 05 | 紅 | The Crimson Maple | — |
| 06 | 滝 | The Falling Water | — |
| 07 | 雪 | The Snow Pass | KOORI-NUSHI (hovering) |
| 08 | 嵐 | The Storm Roof | — |
| 09 | 影 | The Shadow Market | — |
| 10 | 鬼 | The Oni Keep | ONI-GUMA (hovering) |
| 11 | 戒 | The Broken Oath | **KANI** |
| 12 | 灯 | The Hungry Shrine | **MON** |
| 13 | 解 | The Last Chain | **HANO** |

Maps 11–13 are new and built the opposite way round to 01–10: a short approach
that exists only to get the player warm, then a flat arena with nothing in it
but the warden. No spikes on the arena floor, no patrols, no saws. When a fight
has this many moves to read, anything else on screen kills the player instead
of the boss doing it.

## 2. Cast

Portraits are `public/assets/face/`, fight sprites are `public/assets/person/`.
The four faces map one-to-one onto the bible's four characters, and the two
folders use the same names so the art and the character never drift apart.

| id | Name | Portrait | Sprites | Role |
|----|------|----------|---------|------|
| `ren` | REN, the ronin | `rain.jpeg` | the samurai sheets | the player |
| `kani` | KANI, the oathkeeper | `kani.jpeg` | `person/kani/` | guide, then warden 1 |
| `mon` | MON, the lantern-eater | `mon.png` | `person/mon/` | leaves food, then warden 2 |
| `hano` | HANO, the blue armor | `hano.jpeg` | `person/hano/` | the gate, final boss |
| `none` | — | none | — | the world's own voice |

**The plot, in one line each:** Ren wakes chained to a road that goes one way.
Kani walks with him and warns him off, gate by gate, until the gate he is
warning him about is Kani himself. Mon has been leaving him food and cannot
remember why. Hano stands in the last gate wearing armour with nobody inside
it, because whoever wins the fight has always been the one who puts it on. Ren
wins and does not put it on.

### Dialogue budget

The bible caps the whole game at 24 lines. This build spends about 60, still
under five per chapter, because the brief this was built to asked for dialogue
and a plot. The bible's actual rule — every line one breath long, and the story
carried by who blocks the road rather than by prose — is kept.

Two delivery channels, and the split is the point:

- **Scene** (`Dialogue`) — a card between chapters, game stopped, two to six
  lines, portrait and typewriter. Only at the top and tail of a chapter.
- **Bark** (`Bark`) — a line that floats up during play and leaves on its own.
  Nothing pauses, nothing has to be dismissed. Every mid-level beat and
  everything a warden says mid-fight is a bark.

Level beats live in `STORY[n].beats` as `{x, who, text}` and fire once, the
first time the samurai passes that x. Mid-fight lines live in `WARDEN_LINES`,
keyed by what just happened (`start`, `phase2`, `phase3`, `heal`, `down`).

## 3. The warden fights

The three hovering bosses are one loop dressed three ways. A warden is a
character instead: it stands on the floor, it has a move list, and every move
is built out of the same three windows so all three fights read with one pair
of eyes.

```
WIND    the telegraph. Nothing can hurt you yet. The clip plays, an ink ring
        closes around him, a horn rises. The ring completes exactly on the hit.
ACTIVE  the hitbox / the projectiles / the guard. This is what costs a heart.
REST    recovery. He cannot act, cannot block, cannot turn.
        Every one of these fights is won inside this window.
```

**Body contact does not damage the player.** Only the ACTIVE window does. That
is the whole difference in feel: you are allowed to stand next to a warden and
read it, which is what makes learning one possible.

**Poise.** A warden only staggers when it is not committed to a move. A hit
landed into a wind-up still counts, it just does not stop him.

**Phases.** Thirds of health. Each threshold is a hard beat — a roar, a second
of immunity so it cannot be skipped through, a line, and a charm dropped on the
floor. The fight gets harder and the player gets a hit back. The health bar
turns crimson in phase 3 and says which phase it is in.

**Difficulty is ordered by mechanics, not just by numbers.** A scripted bot that
only closes, swings, and jumps on the telegraph kills KANI reliably, kills MON
about half the time, and has never killed HANO.

### 戒 KANI — 12 hp — spacing and the parry

Fast, close, honest. Re-teaches the parry: his kunai are the same deflectable
projectile the caster taught in map 03, at twice the speed, and a kunai sent
back is worth a full slash — so parrying his volley is the *fastest* way
through the fight, not merely the safest.

| move | phase | what it asks |
|------|-------|--------------|
| jab | 1 | short, quick, safe to trade against |
| sweep | 1 | wider and slower — the one to punish |
| blade | 1 | dashes the length of the arena. Jump it. Also his answer to a samurai glued to his chest |
| kunai | 1 | 2 (3 in phase 3) thrown blades. Parry them |
| leap | 3 | he stops pretending and opens with the jump |

### 灯 MON — 15 hp — positioning and the interrupt

Barely moves. Fights with the floor and with her own health bar. Her stakes
erupt out of the shrine slab through their own rise animation, so the telegraph
*is* the hazard — and the pattern is the escalation: phase 1 flanks the player
and leaves the ground under him clear, phase 2 puts one under his feet, phase 3
is five across with only the gaps safe.

**Feast** is the fight. She eats a lantern and takes two health back unless the
player interrupts it — and a hit landed during the meal does double damage and
cancels it. The fight cannot be won by turtling, and that is the lesson.

### 蒼 HANO — 26 hp — patience, then speed

The hardest thing in the game, and hard in a specific way: **it guards.**

- The katana rings off a raised guard. No damage, and the samurai is shoved
  back out of reach.
- The guard only covers the side he is facing — the same side the plate is
  drawn on — and his facing is locked for the whole move. **Getting behind a
  guarding warden is the answer to it.**
- Four hits in quick succession and the guard comes up out of turn, ignoring
  the gap that would have given the player another swing (`punish`).
- A swing that rings off it is answered by the **riposte** the instant the
  guard drops — a fast lunge with almost no telegraph left to read
  (`counterMove`). It is unreachable through the random move pool; the only way
  to ever see it is to hit the guard.

Between them, standing in front of him holding the attack button is not a
strategy. Meanwhile his **slam** sends a shockwave along the floor that
**cannot be parried** — the katana passes straight through it. It is the one
attack in the game that says *jump*, and it exists so that a player who has
learned to parry everything meets one thing that answers otherwise.

Phase 2 adds the lunge and a two-shockwave leap-slam. Phase 3 is the empty
armour: `ruin` chains straight into a second attack with no gap and three
shockwaves out of it.

## 4. Tuning

Everything about a fight is data in `WARDEN_ART`:

- `hp`, `speed`, `runSpeed`, `hold` (preferred standoff), `boxW`/`boxH`
- per move: `wind` / `active` / `rest`, `reach`, `boxH`, `boxY`, `range` band,
  `weight`, `cool`, `phase`, and a `kind` of `melee` / `dash` / `leap` /
  `ranged` / `guard` / `heal`
- `punish` and `counterMove` (hano only)
- wind times scale by phase (×0.9 in phase 2, ×0.78 in phase 3); the gap
  between moves is 0.78s / 0.5s / 0.28s by phase

`clips` entries are `[sheet, frames, fps, ox]`. **`ox` is not optional
polish:** these source sheets are not consistently centred — hano's idle
artwork sits 30px left of its cell centre while his walk is centred — so
without it the character slides sideways whenever the clip changes and his
hurtbox stops agreeing with the body the player is aiming at. Each `ox` is the
measured distance from that sheet's average foot line to the centre of its
cell. Re-measure before swapping any sheet.

`CONFIG.DEBUG_HITBOX = true` outlines a warden's hurtbox in green and its live
attack hitbox in crimson.
