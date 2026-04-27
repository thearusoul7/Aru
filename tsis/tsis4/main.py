from snake import main_menu, game_loop, show_leaderboard

if __name__ == "__main__":
    while True:
        choice = main_menu()

        if choice == "play":
            game_loop()

        elif choice == "leaderboard":
            show_leaderboard()