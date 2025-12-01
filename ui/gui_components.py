"""Componentes GUI para interface gráfica - simplificado"""
import pygame

class Button:
    """Botão interativo"""
    def __init__(self, x, y, width, height, text, color=(70, 130, 180), 
                 hover_color=(100, 160, 210), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.font = pygame.font.Font(None, 32)
        self.is_hovered = False
        
    def draw(self, screen):
        """Desenha o botão"""
        # Sombra
        shadow_rect = self.rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=10)
        
        # Botão
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        
        # Borda
        border_color = (255, 255, 255) if self.is_hovered else (50, 50, 50)
        pygame.draw.rect(screen, border_color, self.rect, 3, border_radius=10)
        
        # Texto
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        """Verifica interação com o botão"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            self.current_color = self.hover_color if self.is_hovered else self.color
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        
        return False

class SessionListItem:
    """Item de sessão na lista - numerado e simples"""
    def __init__(self, x, y, width, height, session_data, rank, is_selected=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.session_data = session_data
        self.rank = rank  # Posição no ranking (1, 2, 3...)
        self.is_selected = is_selected
        self.is_hovered = False
        self.font_title = pygame.font.Font(None, 26)
        self.font_info = pygame.font.Font(None, 22)
        self.font_rank = pygame.font.Font(None, 36)
        
    def draw(self, screen):
        """Desenha item da sessão"""
        # Fundo
        if self.is_selected:
            bg_color = (70, 90, 130)  # Azul quando selecionado
        elif self.is_hovered:
            bg_color = (60, 60, 80)
        else:
            bg_color = (40, 40, 60)
            
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        
        # Borda verde se selecionado
        if self.is_selected:
            border_color = (100, 255, 100)
            border_width = 4
        else:
            border_color = (100, 100, 120)
            border_width = 2
            
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=8)
        
        # Número do ranking
        rank_text = f"#{self.rank}"
        rank_surface = self.font_rank.render(rank_text, True, (200, 200, 200))
        screen.blit(rank_surface, (self.rect.x + 15, self.rect.y + 20))
        
        # ID da sessão (encurtado)
        session_id = self.session_data['id']
        display_id = session_id if len(session_id) < 28 else session_id[:25] + "..."
        
        text_title = self.font_title.render(display_id, True, (255, 255, 255))
        screen.blit(text_title, (self.rect.x + 70, self.rect.y + 12))
        
        # Informações com geração final
        final_gen = self.session_data.get('final_generation', '?')
        info_text = f"Fitness: {self.session_data['best_fitness']:.0f}  |  Geracao: {final_gen}"
        text_info = self.font_info.render(info_text, True, (200, 200, 200))
        screen.blit(text_info, (self.rect.x + 70, self.rect.y + 42))
        
    def handle_event(self, event):
        """Verifica se foi clicado"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        
        return False

class ScrollableList:
    """Lista scrollável de sessões com numeração"""
    def __init__(self, x, y, width, height, items_data, selected_session_id=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.items = []
        self.scroll_offset = 0
        self.item_height = 75
        self.spacing = 10
        self.selected_session_id = selected_session_id
        
        # Cria itens com ranking
        for i, item_data in enumerate(items_data):
            item_y = y + 10 + i * (self.item_height + self.spacing)
            is_selected = (selected_session_id and item_data['id'] == selected_session_id)
            rank = i + 1  # Ranking: 1º, 2º, 3º...
            item = SessionListItem(x + 10, item_y, width - 20, self.item_height, 
                                  item_data, rank, is_selected)
            self.items.append(item)
    
    def update_selection(self, selected_session_id):
        """Atualiza qual sessão está selecionada"""
        self.selected_session_id = selected_session_id
        for item in self.items:
            item.is_selected = (item.session_data['id'] == selected_session_id)
            
    def draw(self, screen):
        """Desenha lista com scroll"""
        # Fundo
        pygame.draw.rect(screen, (30, 30, 50), self.rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), self.rect, 2, border_radius=10)
        
        # Superfície para clipping
        list_surface = pygame.Surface((self.rect.width, self.rect.height))
        list_surface.fill((30, 30, 50))
        
        # Desenha itens
        for item in self.items:
            adjusted_rect = item.rect.copy()
            adjusted_rect.y = item.rect.y - self.rect.y + self.scroll_offset
            
            if -self.item_height < adjusted_rect.y < self.rect.height:
                temp_item = SessionListItem(10, adjusted_rect.y, item.rect.width, 
                                           item.rect.height, item.session_data, 
                                           item.rank, item.is_selected)
                temp_item.is_hovered = item.is_hovered
                temp_item.draw(list_surface)
        
        screen.blit(list_surface, self.rect)
        
    def handle_event(self, event):
        """Gerencia eventos da lista"""
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset += event.y * 20
                
                max_scroll = 0
                min_scroll = -(len(self.items) * (self.item_height + self.spacing) - self.rect.height + 20)
                self.scroll_offset = max(min_scroll, min(max_scroll, self.scroll_offset))
                
        elif event.type == pygame.MOUSEMOTION:
            mouse_y = event.pos[1] - self.rect.y - self.scroll_offset
            for item in self.items:
                item_relative_y = item.rect.y - self.rect.y
                item.is_hovered = (self.rect.collidepoint(event.pos) and 
                                  item_relative_y <= mouse_y < item_relative_y + item.rect.height)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                for item in self.items:
                    if item.is_hovered:
                        return item.session_data['id']
        
        return None

class InfoBox:
    """Caixa de informação"""
    def __init__(self, x, y, width, height, title, info_lines):
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.info_lines = info_lines
        self.font_title = pygame.font.Font(None, 32)
        self.font_info = pygame.font.Font(None, 24)
        
    def draw(self, screen):
        """Desenha caixa de informação"""
        pygame.draw.rect(screen, (40, 40, 60), self.rect, border_radius=10)
        pygame.draw.rect(screen, (100, 150, 200), self.rect, 3, border_radius=10)
        
        title_surface = self.font_title.render(self.title, True, (255, 255, 255))
        screen.blit(title_surface, (self.rect.x + 20, self.rect.y + 15))
        
        y_offset = 55
        for line in self.info_lines:
            info_surface = self.font_info.render(line, True, (200, 200, 200))
            screen.blit(info_surface, (self.rect.x + 20, self.rect.y + y_offset))
            y_offset += 30