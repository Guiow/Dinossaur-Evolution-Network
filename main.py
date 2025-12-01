"""Sistema completo com interface gráfica - ajustado"""
import pygame
import sys
import numpy as np
from game.config import *
from game.engine import GameEngine
from game.renderer import Renderer
from ai.evolutionary_algorithm import EvolutionaryAlgorithm
from ai.session_manager import SessionManager
from ai.neural_network import NeuralNetwork
from ai.population import Agent
from ui.gui_components import Button, ScrollableList, InfoBox

class DinoAIApp:
    """Aplicação principal com interface gráfica"""
    
    def __init__(self):
        pygame.init()
        
        # Configuração de tela
        self.screen_info = pygame.display.Info()
        self.fullscreen = False
        self.windowed_size = (1200, 800)
        self.screen = pygame.display.set_mode(self.windowed_size)
        pygame.display.set_caption("DINO AI - Evolutionary Algorithm")
        
        self.clock = pygame.time.Clock()
        self.session_manager = SessionManager(sessions_dir="sessions")
        
        # Fontes
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 36)
        
    def toggle_fullscreen(self):
        """Alterna entre tela cheia e janela"""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.windowed_size)
            
        return self.screen.get_size()
        
    def draw_background(self):
        """Desenha fundo gradiente"""
        width, height = self.screen.get_size()
        for y in range(height):
            color_value = int(20 + (y / height) * 50)
            pygame.draw.line(self.screen, (color_value, color_value, color_value + 20), 
                           (0, y), (width, y))
    
    def main_menu(self):
        """Menu principal"""
        width, height = self.screen.get_size()
        
        # Botões
        button_width = 400
        button_height = 70
        button_x = (width - button_width) // 2
        start_y = height // 2 - 50
        
        train_button = Button(button_x, start_y, button_width, button_height, 
                             "TREINAR IA", (50, 150, 100), (70, 180, 130))
        watch_button = Button(button_x, start_y + 90, button_width, button_height,
                             "ASSISTIR IA", (100, 100, 200), (130, 130, 230))
        fullscreen_button = Button(button_x, start_y + 180, button_width, button_height,
                                   "TELA CHEIA: OFF", (150, 100, 50), (180, 130, 70))
        quit_button = Button(button_x, start_y + 270, button_width, button_height,
                            "SAIR", (200, 50, 50), (230, 70, 70))
        
        running = True
        while running:
            self.draw_background()
            
            # Título SEM ícone
            title = self.title_font.render("DINO AI", True, (255, 255, 255))
            subtitle = self.subtitle_font.render("Algoritmo Evolutivo", True, (200, 200, 200))
            
            title_rect = title.get_rect(center=(width // 2, 120))
            subtitle_rect = subtitle.get_rect(center=(width // 2, 190))
            
            self.screen.blit(title, title_rect)
            self.screen.blit(subtitle, subtitle_rect)
            
            # Atualiza texto do botão fullscreen
            fullscreen_button.text = f"TELA CHEIA: {'ON' if self.fullscreen else 'OFF'}"
            
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        width, height = self.toggle_fullscreen()
                        button_x = (width - button_width) // 2
                        start_y = height // 2 - 50
                        train_button.rect.x = button_x
                        watch_button.rect.x = button_x
                        fullscreen_button.rect.x = button_x
                        quit_button.rect.x = button_x
                        train_button.rect.y = start_y
                        watch_button.rect.y = start_y + 90
                        fullscreen_button.rect.y = start_y + 180
                        quit_button.rect.y = start_y + 270
                
                if train_button.handle_event(event):
                    return "train"
                if watch_button.handle_event(event):
                    return "watch"
                if fullscreen_button.handle_event(event):
                    width, height = self.toggle_fullscreen()
                    button_x = (width - button_width) // 2
                    start_y = height // 2 - 50
                    train_button.rect.x = button_x
                    watch_button.rect.x = button_x
                    fullscreen_button.rect.x = button_x
                    quit_button.rect.x = button_x
                if quit_button.handle_event(event):
                    return "quit"
            
            # Desenha botões
            train_button.draw(self.screen)
            watch_button.draw(self.screen)
            fullscreen_button.draw(self.screen)
            quit_button.draw(self.screen)
            
            # Instruções
            instructions = self.subtitle_font.render("Pressione F11 para alternar tela cheia", 
                                                     True, (150, 150, 150))
            inst_rect = instructions.get_rect(center=(width // 2, height - 50))
            self.screen.blit(instructions, inst_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return "quit"
    
    def training_selection_menu(self):
        """Menu de seleção de modelo para treinar"""
        width, height = self.screen.get_size()
        
        sessions = self.session_manager.list_all_sessions()
        
        # Botões ABAIXO da lista com espaço
        button_y = height - 80
        start_x = 50
        
        new_train_button = Button(start_x, button_y, 240, 60, 
                                  "TREINAR DO ZERO", (50, 150, 100), (70, 180, 130))
        start_selected_button = Button(start_x + 250, button_y, 240, 60,
                                      "INICIAR", (100, 150, 200), (130, 180, 230))
        delete_button = Button(start_x + 500, button_y, 240, 60,
                              "APAGAR", (200, 50, 50), (230, 70, 70))
        back_button = Button(start_x + 750, button_y, 240, 60,
                            "VOLTAR", (100, 100, 100), (130, 130, 130))
        
        # Lista de sessões com mais espaço para botões
        list_height = height - 320  # Mais espaço abaixo
        session_list = None
        selected_session_id = None
        
        if sessions:
            session_list = ScrollableList(50, 230, width - 100, list_height, 
                                         sessions, selected_session_id)
        
        running = True
        while running:
            self.draw_background()
            
            # Título
            title = self.title_font.render("Selecionar Modelo", True, (255, 255, 255))
            title_rect = title.get_rect(center=(width // 2, 80))
            self.screen.blit(title, title_rect)
            
            # Informações
            if sessions:
                info_text = f"{len(sessions)} sessoes ordenadas por fitness"
                if selected_session_id:
                    selected_data = next((s for s in sessions if s['id'] == selected_session_id), None)
                    if selected_data:
                        info_text = f"SELECIONADA: Fitness {selected_data['best_fitness']:.0f}"
                else:
                    info_text = "Clique em uma sessao para selecionar"
                    
                info_surface = self.subtitle_font.render(info_text, True, (200, 200, 200))
                info_rect = info_surface.get_rect(center=(width // 2, 160))
                self.screen.blit(info_surface, info_rect)
                
                session_list.draw(self.screen)
            else:
                no_sessions = self.subtitle_font.render("Nenhuma sessao encontrada - Inicie do zero!", 
                                                        True, (200, 200, 100))
                no_rect = no_sessions.get_rect(center=(width // 2, height // 2))
                self.screen.blit(no_sessions, no_rect)
            
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, None
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None, None
                    elif event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                
                if new_train_button.handle_event(event):
                    return None, 1
                
                if start_selected_button.handle_event(event) and selected_session_id:
                    try:
                        model_data = self.session_manager.load_session_model(selected_session_id)
                        return model_data, model_data['generation'] + 1
                    except:
                        pass
                
                if delete_button.handle_event(event) and selected_session_id:
                    if self.confirm_dialog("Apagar sessao?", selected_session_id[:30]):
                        self.session_manager.delete_session(selected_session_id)
                        sessions = self.session_manager.list_all_sessions()
                        selected_session_id = None
                        
                        if sessions:
                            session_list = ScrollableList(50, 230, width - 100, list_height, 
                                                         sessions, None)
                        else:
                            session_list = None
                        
                if back_button.handle_event(event):
                    return None, None
                
                if session_list and sessions:
                    clicked_id = session_list.handle_event(event)
                    if clicked_id:
                        if selected_session_id == clicked_id:
                            selected_session_id = None
                        else:
                            selected_session_id = clicked_id
                        
                        session_list.update_selection(selected_session_id)
            
            # Desenha botões
            new_train_button.draw(self.screen)
            if sessions:
                start_selected_button.draw(self.screen)
                delete_button.draw(self.screen)
            back_button.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return None, None
    
    def viewing_selection_menu(self):
        """Menu de seleção de modelo para assistir"""
        width, height = self.screen.get_size()
        
        sessions = self.session_manager.list_all_sessions()
        
        if not sessions:
            self.show_message("Nenhum modelo treinado!", 
                            "Treine primeiro usando o modo de treinamento")
            return None
        
        # Botões ABAIXO da lista
        button_y = height - 80
        start_x = 50
        
        start_selected_button = Button(start_x, button_y, 300, 60,
                                      "ASSISTIR", (100, 150, 200), (130, 180, 230))
        delete_button = Button(start_x + 320, button_y, 300, 60,
                              "APAGAR", (200, 50, 50), (230, 70, 70))
        back_button = Button(start_x + 640, button_y, 300, 60,
                            "VOLTAR", (100, 100, 100), (130, 130, 130))
        
        # Lista
        list_height = height - 320
        selected_session_id = None
        session_list = ScrollableList(50, 230, width - 100, list_height, 
                                     sessions, selected_session_id)
        
        running = True
        while running:
            self.draw_background()
            
            # Título
            title = self.title_font.render("Assistir IA Jogar", True, (255, 255, 255))
            title_rect = title.get_rect(center=(width // 2, 80))
            self.screen.blit(title, title_rect)
            
            info_text = f"{len(sessions)} sessoes disponveis"
            if selected_session_id:
                selected_data = next((s for s in sessions if s['id'] == selected_session_id), None)
                if selected_data:
                    info_text = f"SELECIONADA: Fitness {selected_data['best_fitness']:.0f}"
            else:
                info_text = "Selecione uma sessao"
                
            info_surface = self.subtitle_font.render(info_text, True, (200, 200, 200))
            info_rect = info_surface.get_rect(center=(width // 2, 160))
            self.screen.blit(info_surface, info_rect)
            
            session_list.draw(self.screen)
            
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                
                if start_selected_button.handle_event(event) and selected_session_id:
                    try:
                        return self.session_manager.load_session_model(selected_session_id)
                    except:
                        pass
                
                if delete_button.handle_event(event) and selected_session_id:
                    if self.confirm_dialog("Apagar sessao?", selected_session_id[:30]):
                        self.session_manager.delete_session(selected_session_id)
                        sessions = self.session_manager.list_all_sessions()
                        selected_session_id = None
                        
                        if not sessions:
                            self.show_message("Nenhum modelo restante!", 
                                            "Treine novos modelos")
                            return None
                        
                        session_list = ScrollableList(50, 230, width - 100, list_height, 
                                                     sessions, None)
                        
                if back_button.handle_event(event):
                    return None
                
                clicked_id = session_list.handle_event(event)
                if clicked_id:
                    if selected_session_id == clicked_id:
                        selected_session_id = None
                    else:
                        selected_session_id = clicked_id
                    
                    session_list.update_selection(selected_session_id)
            
            start_selected_button.draw(self.screen)
            delete_button.draw(self.screen)
            back_button.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return None
    
    def confirm_dialog(self, title, message):
        """Diálogo de confirmação"""
        width, height = self.screen.get_size()
        
        dialog_width = 600
        dialog_height = 300
        dialog_x = (width - dialog_width) // 2
        dialog_y = (height - dialog_height) // 2
        
        yes_button = Button(dialog_x + 50, dialog_y + 200, 200, 60,
                           "SIM", (50, 150, 50), (70, 180, 70))
        no_button = Button(dialog_x + 350, dialog_y + 200, 200, 60,
                          "NAO", (200, 50, 50), (230, 70, 70))
        
        running = True
        while running:
            self.draw_background()
            
            # Fundo do diálogo
            dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
            pygame.draw.rect(self.screen, (40, 40, 60), dialog_rect, border_radius=15)
            pygame.draw.rect(self.screen, (200, 100, 100), dialog_rect, 5, border_radius=15)
            
            # Textos
            title_surf = self.subtitle_font.render(title, True, (255, 255, 255))
            title_rect = title_surf.get_rect(center=(width // 2, dialog_y + 70))
            self.screen.blit(title_surf, title_rect)
            
            msg_surf = pygame.font.Font(None, 28).render(message, True, (200, 200, 200))
            msg_rect = msg_surf.get_rect(center=(width // 2, dialog_y + 130))
            self.screen.blit(msg_surf, msg_rect)
            
            # Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                
                if yes_button.handle_event(event):
                    return True
                if no_button.handle_event(event):
                    return False
            
            yes_button.draw(self.screen)
            no_button.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return False
    
    def show_message(self, title, message):
        """Mostra mensagem temporária"""
        width, height = self.screen.get_size()
        
        for _ in range(180):
            self.draw_background()
            
            title_surf = self.title_font.render(title, True, (255, 200, 100))
            msg_surf = self.subtitle_font.render(message, True, (200, 200, 200))
            
            title_rect = title_surf.get_rect(center=(width // 2, height // 2 - 40))
            msg_rect = msg_surf.get_rect(center=(width // 2, height // 2 + 20))
            
            self.screen.blit(title_surf, title_rect)
            self.screen.blit(msg_surf, msg_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
    
    def run(self):
        """Loop principal da aplicação"""
        from training import training_mode
        from viewing import viewing_mode
        
        running = True
        while running:
            choice = self.main_menu()
            
            if choice == "quit":
                running = False
                
            elif choice == "train":
                model_data, start_gen = self.training_selection_menu()
                if start_gen is not None:
                    training_mode(self, model_data, start_gen)
                    
            elif choice == "watch":
                model_data = self.viewing_selection_menu()
                if model_data:
                    viewing_mode(self, model_data)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = DinoAIApp()
    app.run()
