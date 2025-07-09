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

    # 修正：players[1]始终为先手，players[2]为后手
    if player_starts:
        players = {1: agent1, 2: agent2}
        game.current_player = 1  # 确保玩家先手时，当前玩家为玩家
    else:
        players = {1: agent2, 2: agent1}
        game.current_player = 1  # 确保AI先手时，当前玩家为AI

    # 关键修改：在重置游戏前保存当前玩家状态
    initial_current_player = game.current_player
    game.reset()
    # 重置后恢复当前玩家状态
    game.current_player = initial_current_player

    running = True
    while running:
        # AI自动回合
        while isinstance(players[game.current_player], (MCTSAgent, MiniMaxAgent)) and not game.is_terminal():
            pygame.display.set_caption("AI is thinking...")
            ui.draw_board(is_human_turn=False)
            pygame.display.flip()
            action = players[game.current_player].get_action()
            if action:
                game.step(action)
            else:
                break
            pygame.event.clear()
        # 玩家回合
        if game.is_terminal():
            break
        pygame.display.set_caption("Your turn")
        ui.draw_board(is_human_turn=True)
        pygame.display.flip()
        waiting_player = True
        while waiting_player and not game.is_terminal():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting_player = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if isinstance(players[game.current_player], HumanAgent):
                        action = ui.handle_click(event.pos)
                        if action:
                            game.step(action)
                            waiting_player = False
                            if game.is_terminal():
                                running = False
        # 只在回合切换时刷新
        ui.draw_board(is_human_turn=isinstance(players[game.current_player], HumanAgent))
        pygame.display.flip()

    # 游戏结束后等待退出
    while True:
        ui.draw_board(is_human_turn=False)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()