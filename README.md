# **HOW TO PLAY (Tetris)**



## 🚀 Getting Started (First Time Setup)

### What You Need
- **Python 3.7 or newer** installed on your computer
  - Check if you have it: Open Terminal (Mac) or Command Prompt (Windows) and type `python3 --version`
  - Don't have Python? Download it from [python.org](https://www.python.org/downloads/)

### Installation Steps

1. **Download this project**
   - Click the green "Code" button → "Download ZIP"
   - Unzip the folder somewhere easy to find (like your Desktop or Documents)

2. **Open Terminal/Command Prompt**
   - **Mac**: Open "Terminal" app
   - **Windows**: Search for "Command Prompt" or "PowerShell"

3. **Navigate to the game folder**
   ```bash
   cd path/to/Tetris
   ```
   (Replace `path/to/Tetris` with the actual location. Tip: You can drag the folder into Terminal to auto-fill the path!)

4. **Install the game** (one-time setup)
   
   **Mac/Linux:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install pygame supabase python-dotenv
   ```
   
   **Windows:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install pygame supabase python-dotenv
   ```

5. **Run the game!**
   
   **Mac/Linux:**
   ```bash
   .venv/bin/python '!Tetris (PLAY ME).py'
   ```
   
   **Windows:**
   ```bash
   .venv\Scripts\python "!Tetris (PLAY ME).py"
   ```

### Running the Game Later

After the first-time setup, you just need to:
1. Open Terminal/Command Prompt
2. Navigate to the game folder (`cd path/to/Tetris`)
3. Run the game command from step 5 above

### Optional: Leaderboard Setup

To save your scores online, create a file named `.env` in the game folder with:
```
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_key_here
```
(If you don't have this, the game will still work, but scores won't be saved online)

---

## Goal



  Stack falling blocks to complete full horizontal lines.
  
  When a line is filled, it clears and you earn points.
  
  If new pieces can’t spawn because the stack is too high, it’s Game Over.





## Controls (In-Game)



#### Move

    Left Arrow → Move piece left
    
    Right Arrow → Move piece right
    
    Down Arrow → Soft drop (move down faster, one step per press)
    
    D → Hard drop (instantly drops the piece to the lowest valid spot)



#### Rotate

    Up Arrow → Rotate piece
    
    If the rotation would collide, the game attempts a kick rotate (small auto shift to make it fit)



#### Pause

    P → Pause the game



#### Quit

    Q → Quit instantly (works in-game and in menus)





## Lock Delay (Important)

    When your piece touches the ground, it doesn’t always lock immediately.
    
    You have a short window to slide/rotate before it locks.
    
    There’s also a hard “forced lock” timer so you can’t stall forever.

  In your UI:
  
    Red bar = normal lock delay
    
    Blue bar = forced lock timer (absolute max time before the piece locks)





## Main Menu

    Use the mouse to click:
    
    Start Game
    
    Leaderboard
    
    Quit Game
    
    Ultrawide Res / Laptop Res (changes UI scaling)



#### Leaderboard Screen

    M → Back to Main Menu
    
    R → Refresh leaderboard



#### Pause Screen

    R → Resume game
    
    M → Return to Main Menu (resets your run)



#### Game Over Screen

    R → Restart immediately
    
    M → Return to Main Menu
    
    L → Upload score to leaderboard (name entry screen)
    
    Q → Quit



#### Name Entry (Leaderboard Upload)

    Type your name (max length enforced)
    
    Backspace deletes a character
    
    Enter submits your score

