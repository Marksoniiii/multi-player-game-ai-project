"""
双人游戏AI框架主程序
"""

import pygame
import sys
from games.gomoku.gomoku_game import GomokuGame
from games.gomoku.gomoku_ui import GomokuUI
from agents.human_agent import HumanAgent
from agents.mcts_agent import MCTSAgent
from agents.minimax_agent import MiniMaxAgent
import config

def main():
    game = GomokuGame()
    
    # AI先行模式的UI实现
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("选择谁先手")
    font = pygame.font.Font(config.UI_FONT, 32)
    
    player_first_button = pygame.Rect(100, 50, 200, 50)
    ai_first_button = pygame.Rect(100, 120, 200, 50)

    player_starts = None

    while player_starts is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if player_first_button.collidepoint(event.pos):
                    player_starts = True
                elif ai_first_button.collidepoint(event.pos):
                    player_starts = False

        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (100, 100, 100), player_first_button)
        pygame.draw.rect(screen, (100, 100, 100), ai_first_button)
        
        player_text = font.render("玩家先手", True, (255, 255, 255))
        ai_text = font.render("AI先手", True, (255, 255, 255))
        
        screen.blit(player_text, (player_first_button.x + 30, player_first_button.y + 10))
        screen.blit(ai_text, (ai_first_button.x + 50, ai_first_button.y + 10))
        
        pygame.display.flip()

    ui = GomokuUI(game)
    
    human_player = 1 if player_starts else 2
    ai_player = 2 if player_starts else 1

    agent1 = HumanAgent(human_player)
    # agent2 = MCTSAgent(ai_player, game, n_simulations=1000)
    agent2 = MiniMaxAgent(game, ai_player, depth=1)

    players = {1: agent1 if player_starts else agent2, 2: agent2 if player_starts else agent1}
    
    game.reset()
    
    # **核心修复**：重构游戏主循环
    running = True
    while running:
        # 只要当前是AI且游戏未结束，就让AI一直走
        while isinstance(players[game.current_player], (MCTSAgent, MiniMaxAgent)) and not game.is_terminal():
            pygame.display.set_caption("AI is thinking...")
            pygame.display.flip()
            action = players[game.current_player].get_action()
            if action:
                game.step(action)
            else:
                break  # AI无可行动作
            ui.draw_board()
            pygame.display.flip()
            pygame.event.clear()
        # 到这里一定是玩家回合或游戏结束
        if game.is_terminal():
            break
        pygame.display.set_caption("Your turn")
        ui.draw_board()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if isinstance(players[game.current_player], HumanAgent):
                    action = ui.handle_click(event.pos)
                    if action:
                        game.step(action)
                        if game.is_terminal():
                            running = False
        # 每次循环都重绘棋盘和状态
        ui.draw_board()
        pygame.display.flip()

    # 游戏结束后等待
    while True:
        ui.draw_board() # 持续显示最终棋盘
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()