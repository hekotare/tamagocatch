import random
import pygame
import globals as g


p0 = [470, 215]
p1 = [337, 150]
p2 = [245, 160]
p3 = [125, 340]

class ProjectileType:
    Egg  = "Egg"
    Bomb = "Bomb"

class Projectile:
    def __init__(self, type, frame):
        self.projectile_type = type
        self.start_frame = frame # 弾が発生した時刻（フレーム）

# 発射イベント
event_data_list = \
[
    # 時刻（フレーム）, 種類（卵, 爆弾）, 軌道
    [2],
    [4],
    [6],
    [10, ProjectileType.Bomb],
    [14],
    [18],
    [22],
    [24],
    [28, ProjectileType.Bomb],
    [32]
]

class Event:
    def __init__(self):
        self.trigger_frame = 0
        self.projectile_type = ProjectileType.Egg

def create_event_list():
    
    list = []
    prev_event_frame = 0

    for event_data in event_data_list:
        frame = prev_event_frame + event_data[0]
        
        e = Event()

        e.trigger_frame = frame
        e.projectile_type = ProjectileType.Egg
        
        try:
            e.projectile_type = event_data[1]
        except:
            pass
        
        prev_event_frame = frame

        list.append(e)
    
    return list

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

def bezier(a0, b0, a1, b1, a2, b2, a3, b3, t):
    x = \
    a0 * (1 - (3*t) + (3 * (t**2)) - (t**3)) + \
    a1 * t * (3 - (6*t) + (3 * (t**2))) + \
    a2 * (t**2) * (3 - 3*t) + \
    a3 * (t**3)
    y = \
    b0 * (1 - (3*t) + 3 * (t**2) - (t**3)) + \
    b1 * t * (3 - (6*t) + (3 * (t**2))) + \
    b2 * (t**2) * (3 - 3*t) + \
    b3 * (t**3)
    
    return x, y

# return
#   x, y    発射物の座標
#   t       発射物の時刻（0 ~ 1.0)   
def calc_projectile(current_frame, proj):

    elapsed_frame = current_frame - proj.start_frame
    t = elapsed_frame / g.FPS
    
    return *bezier(*p0, *p1, *p2, *p3, t), t

def draw_projectile(surface, proj, current_frame):

    x, y, t = calc_projectile(current_frame, proj)
    
    if (proj.projectile_type == ProjectileType.Egg):
        img_src = g.img_projectile_list[0]
    elif (proj.projectile_type == ProjectileType.Bomb):
        img_src = g.img_projectile_list[1]
    
    surface.blit(img_src, (x - img_src.get_width() * 0.5, y - img_src.get_height() * 0.5))

def load_image():

    folder = 'image/'

    img_src = pygame.image.load(f'{folder}object.png').convert_alpha()
    tmp_list = []

    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (0, 0, 40, 40))
    tmp_list.append(surface)

    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (40, 0, 40, 40))
    tmp_list.append(surface)

    g.img_projectile_list = tmp_list

class Game:

    class State:
        START       = "start"
        MAINGAME    = "maingame"
        RESULT      = "result"
        FAILED      = "failed"
        RETRY       = "retry"

    def __init__(self):
        self.reset()
        self.start_menu()
    
    def reset(self):
        self.event_list = create_event_list()
        self.projectile_list = []
        self.chr_down = False
        self.score = 0
    
    def start_menu(self):
        self.game_state = self.State.START
        self.game_state_frame = 0
    
    def maingame(self):
        self.game_state = self.State.MAINGAME
        self.game_state_frame = 0

        self.reset()
    
    def result(self):
        self.game_state = self.State.RESULT
        self.game_state_frame = 0
    
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
        elif (self.game_state == self.State.RESULT):
            self.update_result()
        elif (self.game_state == self.State.FAILED):
            self.update_failed()
        elif (self.game_state == self.State.RETRY):
            self.update_retry()
    
    def update_start(self):
    
        pressed = pygame.key.get_pressed()
        
        if pressed[pygame.K_SPACE]:
            self.maingame()

    def update_maingame(self):

        self.event_list_proc()

        self.update_chr()

        # 発射物の更新
        for p in self.projectile_list[:]: # スナップショットを取る
        
            t = (self.game_state_frame - p.start_frame) / g.FPS
            
            if (t < 1.0): continue # まだ終点に届いていない
            
            if (self.chr_down):
                # 弾をガードした
                pass
            else:
                # 卵ならスコア加算
                if (p.projectile_type == ProjectileType.Egg):
                        self.score += 1
                
                elif (p.projectile_type == ProjectileType.Bomb):
                    # 爆弾をたべたら失敗！
                    self.failed()
                    self.projectile_list = []
                    return
            
            self.projectile_list.remove(p)
        
        # すべて発射し終えたら終わり
        if (len(self.event_list) == len(self.projectile_list) == 0):
            self.result()
            self.projectile_list = []
    
    def event_list_proc(self):
    
        while (len(self.event_list) != 0):
        
            event = self.event_list[0]
            
            # イベントを発生させるか？
            if (event.trigger_frame <= self.game_state_frame):
                self.event_list.pop(0)
                self.projectile_list.append(\
                    Projectile(event.projectile_type, self.game_state_frame))

            else: # イベントの発生なし
                break

    def update_result(self):
        if (1.0 * g.FPS <= self.game_state_frame):
            self.retry_menu()

    def update_failed(self):
        if (1.0 * g.FPS <= self.game_state_frame):
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
        for proj in self.projectile_list:
            draw_projectile(surface, proj, self.game_state_frame)
        
        # プレイヤーの描画
        
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
    
        window.fill((0, 0, 255))
        
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
