# Setup & Run Pixel Quest - Game Engine Studio

Complete guide to get the game running on your laptop.

---

## 📋 Prerequisites

- **Python 3.8+** (Download from https://www.python.org/downloads/)
- **Git** (Download from https://git-scm.com/)
- **pip** (Usually comes with Python)

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Clone the Repository

```bash
git clone https://github.com/MohamedMahfouzzzzz/Game-Engine.git
cd Game-Engine
```

### Step 2: Install Dependencies

```bash
# For the graphical game (recommended)
pip install pygame

# For full engine features (optional)
pip install -r requirements.txt
```

### Step 3: Run the Game!

```bash
# Graphical version (RECOMMENDED - Full window with graphics)
python games/pixel_quest_graphical.py

# OR text-based version
python games/pixel_quest_simple.py
```

---

## 🎮 Game Controls

| Control | Action |
|---------|--------|
| **LEFT / A** | Move left |
| **RIGHT / D** | Move right |
| **SPACE** | Jump |
| **Goal** | Reach the green square on the right! |

---

## 🎯 Game Objectives

1. **Move Right**: Navigate to the green goal square
2. **Collect Coins**: Yellow squares = 10 points each
3. **Avoid Enemies**: Red squares drain lives
4. **3 Lives**: Don't get hit 3 times!
5. **Score Points**: Collect all 5 coins for maximum score

---

## 📦 What's Included

```
Game-Engine/
├── games/
│   ├── pixel_quest_graphical.py    ⭐ GRAPHICAL VERSION (Recommended!)
│   ├── pixel_quest_simple.py       ⭐ Text-based version
│   └── pixel_quest_standalone.py   Full engine integration
├── engine/                         Core game engine
├── FEATURE_GUIDE.md               Advanced features guide
├── README.md                       Project documentation
└── requirements.txt               Dependencies
```

---

## 🖥️ System Requirements

| Component | Minimum | Recommended |
|-----------|---------|------------|
| **RAM** | 512 MB | 2 GB |
| **Storage** | 100 MB | 500 MB |
| **GPU** | Integrated | Dedicated (optional) |
| **Python** | 3.8 | 3.10+ |

---

## 🐛 Troubleshooting

### "pygame not found" Error

```bash
pip install pygame --upgrade
```

### Game window doesn't appear

- Make sure you're using the graphical version: `pixel_quest_graphical.py`
- Check that pygame is installed: `pip list | grep pygame`
- Try running with verbose mode: `python -u games/pixel_quest_graphical.py`

### Slow performance

- Close other applications
- Update graphics drivers
- Try the text-based version instead: `python games/pixel_quest_simple.py`

### Python not found

- Verify Python is installed: `python --version`
- Add Python to PATH (Windows)
- Use `python3` instead of `python` on some Linux/Mac systems

---

## 📊 Game Engine Features Demonstrated

✅ **Game Engine Capabilities Used:**
- 2D Entity rendering
- Physics simulation (gravity, jumping)
- Collision detection
- Enemy AI (patrolling behavior)
- Score tracking
- Performance monitoring (FPS)
- Game state management
- Input handling
- Real-time rendering

✅ **Advanced Engine Features Available:**
- GD Language (type-safe arrays & dictionaries)
- SQLite database (save/load system)
- AES encryption (secure saves)
- Dialogue system (branching conversations)
- Kanban board (project management)
- Telemetry (performance metrics)
- Export pipeline (multi-platform builds)

---

## 🎓 Learning Resources

1. **Feature Guide**: Read `FEATURE_GUIDE.md` for advanced features
2. **Code Examples**: Check `examples/` directory
3. **API Reference**: See `API_REFERENCE.md` for complete docs
4. **Source Code**: Explore `engine/` for implementation details

---

## 🔧 Development

### Run with Debug Output

```bash
python -v games/pixel_quest_graphical.py
```

### Profile Performance

```bash
python -m cProfile games/pixel_quest_graphical.py
```

### Run Tests

```bash
python -m pytest tests/
```

---

## 📝 Game Development Tips

1. **Start Simple**: Modify `pixel_quest_graphical.py` to add features
2. **Add More Enemies**: Duplicate enemy creation code
3. **Change Colors**: Modify color constants at the top
4. **Adjust Difficulty**: Change `patrol_distance`, `enemy.speed`, or player `jump_force`
5. **Add Levels**: Create multiple game scenes

---

## 🎬 Next Steps

1. ✅ Run the game
2. ✅ Play through and get familiar with it
3. ✅ Examine the source code (`pixel_quest_graphical.py`)
4. ✅ Try modifying colors or difficulty
5. ✅ Read `FEATURE_GUIDE.md` to learn about advanced features
6. ✅ Create your own game!

---

## 📞 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review the code comments in `pixel_quest_graphical.py`
3. Check Python version: `python --version`
4. Verify pygame: `pip install pygame --upgrade`
5. Try the simple text version to isolate issues

---

**Happy Gaming!** 🎮✨

Built with Game Engine Studio - A professional 2D game engine in Python.
