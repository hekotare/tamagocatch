import random
import pygame
import globals as g


def draw_text(surface, str, color, pos):
    text = g.font.render(str, True, color)
    surface.blit(text, pos)

def draw_rect(surface, rect, **kwargs):

    fill = kwargs.get('fill')
    if (fill): pygame.draw.rect(surface, fill, rect)
    
    outline = kwargs.get('outline')
    if (outline):
        width = kwargs.get('width') or 1
        pygame.draw.rect(surface, outline, rect, width=width)

def load_image():
    img_src = pygame.image.load('image/chr.png').convert_alpha()

    surface = pygame.Surface((20, 20), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (0, 0, 20, 20))
    g.img_chr.append(surface)

    surface = pygame.Surface((20, 20), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (20, 0, 20, 20))
    g.img_chr.append(surface)

class Game:

    class State:
        START       = "start"
        MAINGAME    = "maingame"
        FAILED      = "failed"
        RETRY       = "retry"

    def __init__(self):
        self.reset()
        self.start_menu()
    
    def reset(self):
        self.list = [0] * 60
        self.chr_down = False
        self.score = 0
    
    def start_menu(self):
        self.game_state = self.State.START
        self.game_state_frame = 0
    
    def maingame(self):
        self.game_state = self.State.MAINGAME
        self.game_state_frame = 0

        self.reset()
    
    def failed(self):
        self.game_state = self.State.FAILED
        self.game_state_frame = 0 
       
    def retry_menu(self):
        self.game_state = self.State.RETRY
        self.game_state_frame = 0

    def update(self):
        self.game_state_frame += 1

        if (self.game_state == self.State.START):
            self.update_start()
        elif (self.game_state == self.State.MAINGAME):
            self.update_maingame()
        elif (self.game_state == self.State.FAILED):
            self.update_failed()
        elif (self.game_state == self.State.RETRY):
            self.update_retry()
    
    def update_start(self):
    
        pressed = pygame.key.get_pressed()
        
        if pressed[pygame.K_SPACE]:
            self.maingame()

    def update_maingame(self):
        assert len(self.list) == 60, "listおかしい"

        # ダメージ判定
        i = self.list.pop(0)

        if (not self.chr_down):
            if (i == 1): # 卵
                self.score += 1
            elif (i == 2): # ボム
                self.failed()
        else:
            if (i in [1, 2]): # オブジェクトをはじく処理
                pass
        
        # 新しいオブジェクトの追加
        if (self.game_state_frame % 5 == 0):
        
            n = random.randint(0, 5)
            
            if (n == 0):
                self.list.append(1) # 卵
            elif (n == 1):
                self.list.append(2) # ボム
            else:
                self.list.append(0) # なんもなし
        else:
            self.list.append(0) # なんもなし

        self.update_chr()
    
    def update_failed(self):
        if (30 <= self.game_state_frame):
            self.retry_menu()

    def update_retry(self):
    
        pressed = pygame.key.get_pressed()
        
        if pressed[pygame.K_SPACE]:
            self.maingame()
    
    def update_chr(self):
    
        pressed = pygame.key.get_pressed()
        
        if pressed[pygame.K_DOWN]:
            self.chr_down = True
        else:
            self.chr_down = False
    
    def render(self, surface):
    
        # 卵や爆弾オブジェの描画
        for _, value in enumerate(self.list):
        
            if (value == 1): # 卵
                draw_rect(surface, (100 + _ * 4, 300, 4, 10), fill=0xFFFFFF, outline=0x202020, width=2)
            elif (value == 2):
                draw_rect(surface, (100 + _ * 4, 300, 4, 10), fill=0xFF0000, outline=0x202020, width=2)
            else: # value == 0
                pass #なんもしない
        
        # プレイヤーの描画
        img_no = 0 if self.chr_down else 1
        surface.blit(g.img_chr[img_no], (80, 296))
        
        # スコアの描画
        draw_text(surface, str(self.score), (255, 255, 255), (32, 32))
        
        # 各ゲームシーケンスの描画
        if (self.game_state == self.State.START):
            draw_text(surface, "スペースキーを押したら開始！", (255, 128, 128), (100, 400))
        elif (self.game_state == self.State.FAILED):
            draw_text(surface, "失敗・・・！", (128, 96, 64), (100, 400))
        elif (self.game_state == self.State.RETRY):
            draw_text(surface, "スペースキーでリトライ", (128, 96, 64), (100, 400))



def main():
    
    # システムの初期化
    pygame.init()
    window = pygame.display.set_mode((g.WINDOW_WIDTH, g.WINDOW_HEIGHT))
    g.font = pygame.font.Font("C:\Windows\Fonts\meiryo.ttc", 20)

    load_image()

    clock = pygame.time.Clock()
    
    # ゲームの作成
    game = Game()

    while True:
    
        window.fill((0, 0, 0))
        
        game.update()
        game.render(window)
        
        draw_text(window, str(round(clock.get_fps(), 2)), (255, 255, 255), (440, 0))

        pygame.display.update()
        
        clock.tick(g.FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

if __name__ == '__main__':
    main()
