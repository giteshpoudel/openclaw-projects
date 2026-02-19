# COLLABORATION_LOG.md - Snake Game Project

## Project: Browser Snake Game
**Started:** 2025-01-19

---

### 2025-01-19 - Phase 1: Requirements

**PM → BA:**
Please create REQUIREMENTS.md for a browser-based Snake Game with:
1. 4-tile snake start, 64x64 tile grid
2. Heart-shaped coin, random position (not on snake), +1 tile per coin
3. Wrap-around edges (left→right, top→bottom)
4. Self-collision = game over
5. Start screen with "hit any key", score + best score display

**BA → PM:**
✅ REQUIREMENTS.md created with full technical specification including:
- Grid: 64x64, 10px tiles
- Snake: 4 tiles, center-right start
- Coin: ❤️ heart emoji, random spawn
- Wrap-around on all edges
- Self-collision = game over
- Start/Game Over screens with scores
- localStorage for best score

**Status:** Phase 1 COMPLETE

---

### 2025-01-19 - Phase 2: Implementation

**PM → DEV:**
Read REQUIREMENTS.md and implement the Snake Game as a single HTML file.

Requirements summary:
- Single index.html with embedded CSS/JS
- 64x64 grid, 10px tiles = 640x640 canvas
- Snake starts 4 tiles, grows +1 per coin
- Heart coin (❤️) spawns randomly not on snake
- Wrap-around all edges
- Self-collision = game over
- Start screen: "Press ANY KEY to Start", best score
- Game screen: score top-left, best score top-right
- Game over: show final score, update best if beaten

Store in: /workspace/projects/snake-game/index.html

**Status:** IN PROGRESS
