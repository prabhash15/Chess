# PBL-DAA Chess Project
This project is a chess game built using Python and Pygame. It supports Human vs Human and Human vs Bot modes.
The main objective is to demonstrate how a chess bot can be built using DAA/AI algorithms such as move generation, board evaluation, Minimax, and Alpha-Beta pruning. The bot is kept simple: good enough for casual play and project demonstration, but not a professional chess engine.

## How to Run
```bash
python3 main.py
```

## Basic Controls
| Key / Action | Purpose |
| --- | --- |
| Mouse drag and drop | Move pieces |
| B | Toggle Human vs Bot / Human vs Human |
| 1, 2, 3, 4 | Select Easy, Normal, Medium, Hard bot |
| R | Reset game |
| Q | Quit game |

Default mode: Human plays White, bot plays Black, difficulty is Medium.
## Project Structure
```text
PBL-DAA/
├── main.py
├── src/
│   ├── ai.py, board.py, game.py, piece.py
│   ├── square.py, move.py, dragger.py
│   └── const.py, config.py, color.py, theme.py, sound.py
└── assets/
    ├── images/
    └── sounds/
```
# Main Modules
## main.py
`main.py` is the entry point of the game. It connects the Pygame window, player input, board logic, and AI logic.
Important responsibilities:
- Starts Pygame and opens the chess window.
- Creates the `Game` object and the `AI` object.
- Runs the main event loop.
- Handles mouse dragging and dropping for human moves.
- Handles keyboard input for reset, quit, mode, and difficulty.
- Calls the bot after the human makes a valid move in Human vs Bot mode.

Important functions:

- `mainloop()` keeps the game running, draws the board, reads events, validates moves, and updates the display.
- `play_ai_move()` asks the bot for the best move, applies it, changes the turn, and redraws the board.
- `set_ai_difficulty()` changes the bot search depth.
In short, `main.py` controls the overall program flow.

## src/board.py
`board.py` is one of the most important modules because it stores the chessboard and implements the chess rules.
Important responsibilities:
- Creates the 8x8 board.
- Places all pieces at their starting positions.
- Moves pieces from one square to another.
- Checks whether a move is valid.
- Generates legal moves for each piece.
- Handles promotion, en passant, and castling.
- Prevents moves that leave the king in check.

Important functions:

- `move(piece, move)` updates the board after a move. It also handles captures, promotion, en passant, castling, and last move tracking.
- `calc_moves(piece, row, col, bool=True)` generates the legal moves of a piece. It contains different logic for pawn, knight, bishop, rook, queen, and king.
- `in_check(piece, move)` checks whether a possible move would put or leave the king in check.
This module is critical for the AI because the bot depends on `calc_moves()` to know which moves are legal before it can choose the best one.

## src/ai.py
`ai.py` contains the chess bot. This is the most important module from the AI and DAA point of view.
Important responsibilities:
- Gets all legal moves for the bot.
- Evaluates board positions.
- Selects moves using Random, Greedy, Minimax, and Alpha-Beta logic.
- Temporarily applies moves while searching future positions.
- Restores the board after testing each move.

Important functions:
- `get_all_moves(board, color)` returns every legal move for a side.
- `evaluate(board)` gives a numeric score to the board from the bot's point of view.
- `get_random_move(board)` chooses any legal move randomly.
- `get_greedy_move(board)` chooses the best immediate move.
- `get_best_move(board)` selects the final move using Alpha-Beta Minimax.
- `minimax(board, depth, maximizing)` contains the basic Minimax algorithm.
- `alpha_beta(board, depth, alpha, beta, maximizing)` improves Minimax by pruning unnecessary branches.
- `make_temp_move()` and `undo_temp_move()` let the AI test moves without permanently changing the board.

# AI Algorithm Explanation
## Board Evaluation
The AI gives every board position a score. Positive means good for the bot; negative means good for the human.
The evaluation mainly uses material values:
| Piece | Value |
| --- | --- |
| Pawn | 1 |
| Knight | 3 |
| Bishop | 3.001 |
| Rook | 5 |
| Queen | 9 |
| King | 10000 |
A small bonus is also given for controlling centre squares. This keeps the bot simple but slightly more logical.

## Random Move
Used for Easy difficulty. The bot generates all legal moves and randomly picks one.
Complexity: `O(m)`, where `m` is the number of legal moves.
This is weak, but it is useful as the simplest bot level.

## Greedy Move
The bot tests every legal move, evaluates the board immediately after that move, and chooses the move with the best score.
Complexity: `O(m)`.
This is better than random because it can capture valuable pieces, but it does not think about the opponent's reply.

## Minimax
Minimax is the main decision-making algorithm. It assumes the bot tries to maximize the score and the human tries to minimize it.
The algorithm searches future moves up to a fixed depth. At the final depth, the board is evaluated and the result is passed back up the search tree.
Complexity: `O(b^d)`, where `b` is the branching factor and `d` is the search depth. In chess, `b` is often around 20 to 35, so deeper search becomes expensive quickly.

## Alpha-Beta Pruning
Alpha-Beta pruning optimizes Minimax. It gives the same result as Minimax but avoids searching branches that cannot affect the final decision.
- `alpha` is the best score already found for the maximizing player.
- `beta` is the best score already found for the minimizing player.
Worst-case complexity: `O(b^d)`. Best-case complexity: about `O(b^(d/2))`.
This makes the bot faster and allows a better difficulty level without making the game too slow.

## Difficulty Levels
| Difficulty | Depth | Behaviour |
| --- | --- | --- |
| Easy | 0 | Random moves |
| Normal | 1 | Looks at immediate result |
| Medium | 2 | Searches one move deeper |
| Hard | 3 | Stronger, but slower |
The bot is good enough for project demonstration and casual play. It does not use opening books, endgame tables, advanced positional evaluation, or machine learning.

## AI Move Flow
```text
Human moves White piece
↓
Board validates and applies the move
↓
Turn changes to Black
↓
main.py calls play_ai_move()
↓
AI gets all legal Black moves
↓
AI searches using Alpha-Beta Minimax
↓
Best move is selected and applied
↓
Turn changes back to White
```
## Move Simulation Optimization
During search, the AI must test many possible moves. Copying the whole board every time would be slow.
Instead, the bot uses `make_temp_move()` and `undo_temp_move()`. It temporarily makes a move, evaluates or searches the position, then restores the board exactly as it was.

# Supporting Modules
## src/game.py
Manages game state and drawing. It stores the board, current player, dragger, theme, and sound system. It is important for display, but not the main AI logic.
## src/piece.py
Defines Pawn, Knight, Bishop, Rook, Queen, and King. Each piece stores its color, value, image path, movement state, and generated moves.
## src/square.py
Represents one board square. It checks whether a square is empty, has a friendly piece, has an enemy piece, or is inside the board.
## src/move.py
Represents a move from an initial square to a final square. It is used for validation, comparison, and applying moves.
## src/dragger.py
Handles mouse dragging by tracking the selected piece and mouse position.
## src/const.py
Stores fixed values such as rows, columns, screen size, and square size.
## src/config.py, color.py, theme.py, sound.py
These support visuals, colours, themes, and sound. They improve the user experience but are less important for explaining the chess algorithms.

# Overall Program Flow
```text
Start main.py
↓
Create Game, Board, and AI objects
↓
Draw board and pieces
↓
Wait for human input
↓
If move is valid, update board
↓
If Human vs Bot mode is active, AI plays Black move
↓
Repeat until reset or quit
```
# Conclusion
The most important files are `main.py`, `board.py`, and `ai.py`. `main.py` controls the game loop, `board.py` handles chess rules and legal moves, and `ai.py` implements the bot using evaluation, Minimax, and Alpha-Beta pruning.
The final bot is intentionally simple, understandable, and suitable for a project focused on algorithm implementation rather than professional chess strength.
