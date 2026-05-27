import pygame
import sys
from src.const import *
from src.game import Game
from src.square import Square
from src.move import Move
from src.ai import AI


class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.game = Game()
        self.ai = AI(color='black', depth=2)
        self.vs_ai = True
        self.difficulty = 'Medium'
        self.update_window_caption()

    def update_window_caption(self):
        mode = 'Human vs Bot' if self.vs_ai else 'Human vs Human'
        pygame.display.set_caption(f'Chess - {mode} - {self.difficulty}')

    def toggle_game_mode(self):
        self.vs_ai = not self.vs_ai
        self.update_window_caption()

        if self.vs_ai and self.game.next_player == self.ai.color:
            self.play_ai_move()

    def set_ai_difficulty(self, difficulty, depth):
        self.difficulty = difficulty
        self.ai.depth = depth
        self.update_window_caption()

    def play_ai_move(self):
        game = self.game
        board = game.board

        if not self.vs_ai or game.next_player != self.ai.color:
            return

        ai_piece, ai_move = self.ai.get_best_move(board)

        if ai_piece is None or ai_move is None:
            return

        captured = board.squares[ai_move.final.row][ai_move.final.col].has_piece()

        pygame.time.delay(300)
        board.move(ai_piece, ai_move)
        board.set_true_en_passant(ai_piece)
        game.play_sound(captured)
        game.next_turn()

        game.show_bg(self.screen)
        game.show_last_move(self.screen)
        game.show_pieces(self.screen)
        pygame.display.update()

    def mainloop(self):
        
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger

        while True:
            # show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():

                # click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)

                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE

                    # if clicked square has a piece ?
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece
                        # valid piece (color) ?
                        if piece.color == game.next_player:
                            if self.vs_ai and piece.color == self.ai.color:
                                continue

                            board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)
                            # show methods 
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                
                # mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE

                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        # show methods
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)
                
                # click release
                elif event.type == pygame.MOUSEBUTTONUP:
                    
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        # create possible move
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(released_row, released_col)
                        move = Move(initial, final)

                        # valid move ?
                        if board.valid_move(dragger.piece, move):
                            # normal capture
                            captured = board.squares[released_row][released_col].has_piece()
                            board.move(dragger.piece, move)

                            board.set_true_en_passant(dragger.piece)                            

                            # sounds
                            game.play_sound(captured)
                            # next turn
                            game.next_turn()

                            # stop dragging before drawing, otherwise show_pieces
                            # skips the piece that was just placed
                            dragger.undrag_piece()

                            # show the human move before AI calculations begin
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)
                            game.show_hover(screen)
                            pygame.display.update()

                            self.play_ai_move()
                            continue
                    
                    dragger.undrag_piece()
                
                # key press
                elif event.type == pygame.KEYDOWN:
                    
                    # changing themes
                    if event.key == pygame.K_t:
                        game.change_theme()

                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger
                        self.update_window_caption()

                    if event.key == pygame.K_b:
                        self.toggle_game_mode()

                    if event.key == pygame.K_1:
                        self.set_ai_difficulty('Easy', 0)

                    if event.key == pygame.K_2:
                        self.set_ai_difficulty('Normal', 1)

                    if event.key == pygame.K_3:
                        self.set_ai_difficulty('Medium', 2)

                    if event.key == pygame.K_4:
                        self.set_ai_difficulty('Hard', 3)
                    
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            pygame.display.update()


if __name__ == '__main__':
    main = Main()
    main.mainloop()