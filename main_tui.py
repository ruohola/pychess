"""The text based/TUI version of the chess game."""

from utils import InvalidMoveError
from game import Game


def main():
    game = Game()
    
    clear()
    print(
        "Welcome to chess.\n"
        "Please enter your moves as `a2 a4`"
        f"\n\n{game}\n"
    )
    player = game.current_player
    while True:
        move = input(f"{player}'s move: ")
        try:
            # Handle a normal move.
            try:
                # Only this line in the try-block, so we don't accidentally catch any inner ValueErrors.
                fr, to = move.lower().split()
            except ValueError:
                raise InvalidMoveError from None
            player.move(fr, to)
            
            # Handle possible pawn promotion.
            while player.promotion:
                clear()
                print(game)
                piece = input(f"Enter piece to promote to (queen, knight, rook, or bishop): ")
                try:
                    player.promote(piece)
                except InvalidMoveError:
                    clear()
                    print(f"{game}\nInvalid promotion, try again.")
            
        except InvalidMoveError:
            clear()
            print(f"{game}\nInvalid move, try again.")
        else:
            clear()
            print(f"{game}\n")
            player = game.next_player()

        
def clear():
    print("\n" * 20)


if __name__ == "__main__":
    main()
