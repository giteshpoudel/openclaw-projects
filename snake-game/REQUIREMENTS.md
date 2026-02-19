# Snake Game v2 - Technical Specification (UPDATED)

## Project Overview
- **Project Name:** Snake Game v2
- **Type:** Browser-based HTML5 Game
- **Core Functionality:** Classic snake game with speed mechanics, wrap-around, and heart collectibles
- **Target Users:** Casual gamers, browser users

---

## 1. Game Specifications

### Grid & Display
- **Grid Size:** 50 x 50 tiles (reduced from 64x64)
- **Tile Size:** 12px x 12px (rendered at 600x600 pixels)
- **Canvas:** HTML5 Canvas element
- **Play Area:** White background with grey fine-line grid
- **Game Background (outside box):** #0f0f23 (dark/black)

### Snake
- **Initial Length:** 4 tiles
- **Initial Position:** Center of grid, facing right
- **Growth:** +1 tile per coin collected
- **Movement:** Continuous at fixed speed, direction change via arrow keys

### Speed Mechanics (NEW)
1. **Key Hold Acceleration:** While user holds arrow key in current direction, speed increases 1.5x
2. **Growth-based Acceleration:** Every 10 hearts collected (snake grows by 10), speed increases by 10%
   - Base speed: 120ms per frame
   - Growth speed bonus: +10% per 10 coins (compounding)
   - Hold speed bonus: +50% while holding

### Coin (Heart)
- **Symbol:** ❤️ (heart emoji) or custom heart shape
- **Spawn Rules:** Random tile, must NOT be on snake body
- **Effect:** +1 to snake length, +10 points to score

### Edge Wrapping
- Snake exiting left → appears on right
- Snake exiting right → appears on left
- Snake exiting top → appears on bottom
- Snake exiting bottom → appears on top

### Collision
- **Self-collision:** Game Over (snake head hits any body segment)
- **Wall:** No death (wrap-around instead)

---

## 2. UI/UX Specification

### Layout
- **Outer Container:** Dark background (#0f0f23)
- **Play Area Box:** 
  - White background (#ffffff)
  - Grey fine-line grid: #e0e0e0, 1px lines
  - Centered in viewport
  - 600x600px (50 tiles × 12px)

### Start Screen
- Dark overlay covering game area
- Title: "🐍 SNAKE"
- Subtitle: "Press ANY KEY to Start"
- Best Score displayed: "Best: X"
- Current Score: "Score: 0" (visible but 0)

### Game Screen
- Canvas centered within white grid box
- Score display: Top-left corner (inside box)
- Best Score: Top-right corner (inside box)
- Speed indicator: Shows current speed multiplier

### Game Over Screen
- Same overlay style as start
- Title: "GAME OVER"
- Final Score displayed
- "Press ANY KEY to Restart"
- Best Score updated if beaten

### Visual Design
- **Outer Background:** #0f0f23 (dark)
- **Play Area Background:** #ffffff (white)
- **Grid Lines:** #e0e0e0 (light grey, 1px)
- **Snake Head:** #00ff88 (bright green)
- **Snake Body:** #00cc6a (slightly darker green)
- **Coin/Heart:** #ff4757 (red/pink)
- **Text:** #1a1a2e (dark), font: monospace

---

## 3. Data Structures

### Snake
```javascript
snake = [
  {x: 25, y: 25},  // Head (center of 50x50 grid)
  {x: 24, y: 25},
  {x: 23, y: 25},
  {x: 22, y: 25}   // Tail (4 tiles initially)
]
```

### Speed Calculation
```javascript
baseSpeed = 120  // ms per frame
growthBonus = Math.floor(heartsCollected / 10) * 0.10  // 10% per 10 hearts
holdBonus = isKeyHeld ? 0.5 : 0  // 50% boost while holding
currentSpeed = baseSpeed / (1 + growthBonus + holdBonus)
```

### Coin Position
```javascript
coin = {x: random(0-49), y: random(0-49)}
// Must verify not on snake body
```

### Game State
```javascript
state = "start" | "playing" | "gameover"
score = 0
heartsCollected = 0
bestScore = localStorage.getItem("snakeBestScore") || 0
direction = {x: 1, y: 0}  // Moving right initially
nextDirection = {x: 1, y: 0}
isKeyHeld = false  // Track if arrow key is being held
gameSpeed = 120   // ms per frame (base)
```

---

## 4. Controls

- **Arrow Keys:** Change snake direction
- **Key Hold:** While holding arrow key in current direction, speed increases 1.5x
- **Any Key:** Start game / Restart after game over
- **Restriction:** Cannot reverse direction (e.g., can't go left if currently going right)

---

## 5. Game Loop

1. Check key hold status, update speed accordingly
2. Update direction from input buffer
3. Calculate new head position (with wrap-around)
4. Check self-collision → Game Over if hit
5. Check coin collision → Add segment, spawn new coin, add score, increment heartsCollected
6. Check heartsCollected for speed increase
7. Move snake (add new head, remove tail unless grew)
8. Render frame
9. Repeat at currentSpeed interval

---

## 6. Acceptance Criteria

- [ ] Game starts on any key press from start screen
- [ ] Snake starts with exactly 4 segments
- [ ] Grid is 50x50 tiles (reduced from 64)
- [ ] Play area has white background with fine grey grid lines
- [ ] Area outside play box is dark/black
- [ ] Heart coin appears randomly, never on snake
- [ ] Eating coin: snake grows by 1, score +10
- [ ] **Holding arrow key** in current direction → 1.5x speed
- [ ] **Every 10 hearts** collected → +10% speed (compounding)
- [ ] Snake wraps around all 4 edges
- [ ] Self-collision triggers game over
- [ ] Score displays during gameplay
- [ ] Speed indicator shows current multiplier
- [ ] Best score persists across sessions (localStorage)
- [ ] Game over screen shows final score
- [ ] Can restart after game over

---

## 7. File Structure

```
/projects/snake-game/
├── REQUIREMENTS.md    (this file - v2)
├── index.html         # Single file containing HTML + CSS + JS (v2)
└── COLLABORATION_LOG.md
```

---

## 8. Changelog (v1 → v2)

| Feature | v1 | v2 |
|---------|----|----|
| Grid Size | 64x64 | 50x50 |
| Speed on Key Hold | N/A | 1.5x |
| Speed on Growth | N/A | +10% per 10 hearts |
| Play Area BG | Dark | White with grey grid |
| Outer BG | Dark | Dark (same) |
