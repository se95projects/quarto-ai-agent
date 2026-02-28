# What we’re building

A CLI (command-line interface) is a program that:
- Prints the current state (board, whose turn, etc.)
- Reads what the user types
- Updates state (using your engine) and repeats until the game ends

So the core is: display → read input → apply move → repeat.

# Break it into small steps

- Display the board – given a GameState, print the 4×4 grid so you can see pieces (or empty cells).
- Display “whose turn” and what they must do – e.g. “Player 1: choose a piece to give” vs “Player 0: choose where to place”.
- Read and parse input – turn user text into a (row, col) or a Piece the engine understands.
- Game loop – start from an initial state, then in a loop: display → get input → make_move → check_winner (and draw), exit when done.

# We’ll do step 1 first.

## Step 1: Display the board

Goal: Write a function that takes the current board (or full GameState) and prints the 4×4 grid in the terminal.
Decisions you need to make:
- How do you want to show a cell?
    - Empty: e.g. "." or "__".
    - With a piece: a piece has 4 booleans (height, color, shape, top). You need a short, readable code for each of the 16 pieces (e.g. 4 letters: Tall/Short, Light/Dark, Square/Round, Hollow/Solid). Pick a scheme and stick to it.
- How do you want to show rows and columns?
    - Option A: labels like 0 1 2 3 and 0: . . . . so players can say “row 1, col 2”.
    - Option B: no labels and document that input is “row col” (e.g. 1 2).

Concrete task:
- Create a file cli.py (or main.py) in the project root.
- In that file, write a function, e.g. def show_board(state): (or def show_board(board): if you prefer to pass only the board).
- Inside it, loop over state.board.grid (it’s list[list[Optional[Piece]]]). For each cell, print your “empty” symbol or the code for the piece.
- Add a if __name__ == "__main__": block that builds a single GameState by hand (empty board, remaining_pieces can be a small list or empty for now), and call show_board(state). Run the file and confirm you see a 4×4 grid.
- Hint: To “code” a Piece as a string, use its four attributes. For example one convention is: first char = T if height else S, second = L if color else D, etc. You can write a small helper def piece_to_code(p: Piece) -> str and use it for both the board and later for listing pieces.

Once you have the board printing the way you like, we can do step 2 (showing whose turn it is and whether they “select piece” or “place piece”), then input parsing, then the full loop. If you paste your show_board (and piece_to_code if you have it) or describe what you tried, we can refine it step by step without me writing the full solution for you.

---

## Step 2: Display whose turn and what they must do

Goal: After (or before) the board, print a line that says which player's turn it is and whether they must "choose a piece to give" or "choose where to place" the selected piece.

Decisions you need to make:
- Where do you show this line?
  - Option A: one line above the board (e.g. "Player 1: choose a piece to give" then the grid).
  - Option B: one line below the board.
  - Option C: both (e.g. short prompt above, reminder below). Pick one and stick to it.
- Wording: use "Player 0" / "Player 1", or "Player 1" / "Player 2"? Keep it consistent with how you'll document input (e.g. "row col" 0–3).
- For PLACE_PIECE, do you want to show the selected piece? e.g. "Player 0: choose where to place [TLSS]". Optional but helps.

Concrete task:
- In cli.py, add a function, e.g. `def show_turn(state: GameState) -> None`, that prints a single line.
- Use `state.current_player` and `state.current_phase` (e.g. `GamePhase.SELECT_PIECE` vs `GamePhase.PLACE_PIECE`). If phase is SELECT_PIECE, print that they must choose a piece to give; if PLACE_PIECE, print that they must choose where to place (and optionally show `state.selected_piece` with `piece_to_code`).
- In your `if __name__ == "__main__":` block, call both `show_turn(state)` and `show_board(state)` in the order you chose. Build two states by hand: one in SELECT_PIECE (e.g. with some remaining_pieces) and one in PLACE_PIECE (e.g. with selected_piece set), run the file, and confirm you see the right message for each.
- Hint: You can do it with a simple `if state.current_phase == GamePhase.SELECT_PIECE: ... else: ...`, or a small dict from phase to message. No input yet—just display.

Once this looks good, step 3 is reading and parsing input (piece choice vs row col).

---

## Step 3: Read and parse input

Goal: Turn what the user types into the form the engine expects: during SELECT_PIECE, a `Piece` (for `piece_to_give`); during PLACE_PIECE, a `(row, col)` (for `placement`). Invalid input should be handled without crashing (e.g. print a short message and ask again, or return something that the caller can treat as "invalid").

Decisions you need to make:
- **Piece input:** Players already see 4-letter codes (e.g. TLSS). Do you accept exactly that (e.g. "TLSS") and parse it back to a `Piece`, or allow variations (e.g. case-insensitive, or "t l s s" with spaces)? Stick to one rule and document it.
- **Placement input:** Two numbers for row and column. Format: "row col" (e.g. "1 2") or "row,col" or two separate prompts? Match the labels you use on the board (0–3).
- **Validation:** On invalid input, do you re-prompt in the same function (loop until valid) or return a sentinel (e.g. `None`) and let the caller re-prompt? Either is fine; pick one so the game loop stays simple.
- **Quit / help:** Optional for step 3: do you want a special command (e.g. "q" to quit, "h" for help) or keep step 3 to "only parse one piece or one placement"?

Concrete task:
- **Parse piece:** Write a function, e.g. `def parse_piece(text: str) -> Piece | None`, that takes a string (e.g. "TLSS") and returns the corresponding `Piece`, or `None` if the string is invalid. Map each letter to a boolean (T→height True, S→height False; L→color True, D→False; S→shape True, R→False; H→top True, S→top False). Reject wrong length or unknown letters.
- **Parse placement:** Write a function, e.g. `def parse_placement(text: str) -> tuple[int, int] | None`, that takes a string (e.g. "1 2") and returns `(row, col)` in 0–3, or `None` if invalid. Strip and split; reject non-integers or out-of-range.
- **Get one valid input (optional but useful):** Either a function that loops until the user enters a valid piece (or placement) and returns it, or keep "read line → parse → if None print error and return None" and let the game loop re-prompt. Your choice.
- **Integrate with engine:** You don't need the full game loop yet. To test step 3, you can call `input("...")`, then `parse_piece` or `parse_placement` depending on phase, and print the result (or "Invalid, try again"). Use `get_legal_piece_selections(state)` and `get_legal_placements(state)` when you want to validate that the piece is in the remaining list or the cell is empty (you can do that in step 3 or in the loop in step 4).
- Hint: For `parse_piece`, a small dict or if/else for each of the 4 positions is enough. For `parse_placement`, `line.strip().split()` then `int(x)` in a try/except, and check `0 <= row <= 3` and `0 <= col <= 3`. Optionally check `(row, col) in get_legal_placements(state)` in the loop.

Once parsing works (you can run a tiny test that prompts once for a piece and once for a placement and prints the result), step 4 is the game loop: display → get input → make_move → check_winner (and draw), exit when done.

---

## Step 4: Game loop

Goal: Run the game from start to finish. Loop: show board and turn → get input (piece or placement) → call make_move → check for winner or draw → repeat until the game ends, then print the result and exit.

Decisions you need to make:
- **Initial state:** Build a starting GameState: board empty (e.g. `Board.empty()`), all 16 pieces in `remaining_pieces`, `current_phase = GamePhase.SELECT_PIECE`, `selected_piece = None`, `current_player = 0` (or 1). Use the same piece-coding order as your parser (e.g. `product([True, False], repeat=4)` for the 16 pieces).
- **When to check for win/draw:** After each `make_move` (only after a placement, since that’s when the board changes). Call `check_winner(state)`; if it returns a player index, the game is over. Optionally: if the board is full and there is no winner, treat that as a draw (if your engine doesn’t already do that).
- **Mutation vs reassignment:** Your `make_move` mutates the given state and returns it. So you can either `state = make_move(state, ...)` or just `make_move(state, ...)` and keep using `state`; either way, use the updated state for the next iteration and for `check_winner`.
- **Quit command:** Optional: allow e.g. "q" during input to exit the loop and quit the program without crashing.

Concrete task:
- **Loop body:** In `if __name__ == "__main__":` (or a `def main():` that you call from there), create the initial GameState as above. Then `while True`: (1) show board and turn (`show_board(state)`, `show_turn(state)`); (2) if phase is SELECT_PIECE, call `parse_piece(get_legal_piece_selections(state))` to get a piece, then `make_move(state, piece_to_give=piece)` (or reassign state); (3) if phase is PLACE_PIECE, call `parse_placement(get_legal_placements(state))` to get `(row, col)`, then `make_move(state, placement=(row, col))`; (4) after each move, call `check_winner(state)`—if not None, print who won and `break`; (5) optionally, if the board is full and winner is None, print "Draw" and `break`. After the loop, you’re done.
- **Order of operations:** Get input and make_move *after* showing the state for the current turn. After make_move, check winner before the next iteration so you don’t show the board again for a finished game.
- Hint: Use `if state.current_phase == GamePhase.SELECT_PIECE:` to decide whether to call `parse_piece` or `parse_placement`. Handle `make_move` raising (e.g. if the engine raises on invalid move) only if you don’t already validate in parse_*; otherwise you can assume the move is valid.

Once the loop runs and you can play to a win (or draw), the CLI is complete. You can later add a "play again?" or refactor into a `main()` for clarity.