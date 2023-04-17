import random
import pygame
import globals as g
import math

p0 = [470, 215]
p1 = [337, 150]
p2 = [245, 160]
p3 = [125, 340]

class ProjectileType:
    Egg  = "Egg"
    Bomb = "Bomb"

class Projectile:
    def __init__(self, type, frame, move_type):
        self.projectile_type = type
        self.start_frame = frame # 弾が発生した時刻（フレーム）
        self.move_type  = move_type
        self.rotate = random.randint(-45, 45) # 初期の姿勢

class PlayerState:
    Eat   = "eat"
    Guard = "guard"
    Damage = "damage"
    Dead  = "dead"

class MoveType:
    Normal      = 1     # 通常の球
    Yamanari    = 2     # 山なりの球
    OutField    = 3     # ガードしてはじかれた球
    
    def in_field(move_type):
        return move_type in [MoveType.Normal, MoveType.Yamanari]

# 発射イベント
event_data_list = \
[
    # 時刻（フレーム）, 種類（卵, 爆弾）, 軌道
    # 値がNone, 0などの場合は、デフォルト値がセットされる
    [10],
    [10, None, MoveType.Yamanari],
    [ 5],
    [10, ProjectileType.Bomb],
    [10],
    [10],
    [20],
    [20],
    [20, ProjectileType.Bomb],
    [10],
    [30],
    [10, ProjectileType.Bomb],
    [10],
    [10],
    [10],
    [10, None, MoveType.Yamanari],
    [16, ProjectileType.Bomb],
    [10, ProjectileType.Bomb],
    [10],
    [10],
    [10, ProjectileType.Bomb],
    [10],
    [10],
    [10],
    [ 5],
    [10, ProjectileType.Bomb],
    [ 5],
    [ 5],
    [20],
    [10],
    [5, ProjectileType.Bomb, MoveType.Yamanari],
    [6],
    [10],
    [10, ProjectileType.Bomb],
    [14],
    [30],
    [ 6, ProjectileType.Bomb],
    [10],
    [10],
    [20],
]

class Event:
    def __init__(self):
        self.trigger_frame = 0
        self.projectile_type = ProjectileType.Egg
        self.move_type = MoveType.Normal

def clamp(n, min_value, max_value):
    return max(min_value, min(n, max_value))

def create_event_list():
    
    list = []
    prev_event_frame = 0

    for event_data in event_data_list:
        frame = prev_event_frame + event_data[0]
        
        e = Event()

        e.trigger_frame = frame
        e.projectile_type = ProjectileType.Egg

        try:
            e.projectile_type = event_data[1] or e.projectile_type
            e.move_type = event_data[2] or e.move_type
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

# ピッチャーの手(470, 215) - キャラの口(125, 340)
# けっこーはやいボール
def move_normal(elapsed_frame):
    p0 = [470, 215]
    p1 = [337, 150]
    p2 = [245, 160]
    p3 = [125, 340]
    
    t = elapsed_frame / (g.FPS * 0.8)
    t2 = clamp(t, 0, 1)
    
    x, y = bezier(*p0, *p1, *p2, *p3, t2)
    
    return x, y, t2

# 山なりボール
def move_yamanari(elapsed_frame):
    p0 = [470, 215]
    p1 = [305,  50]
    p2 = [180,  90]
    p3 = [125, 340]
    
    t = elapsed_frame / (g.FPS * 1.2)
    t2 = clamp(t, 0, 1)
    
    x, y = bezier(*p0, *p1, *p2, *p3, t2)
    
    return x, y, t2

# ガードされた弾
def move_outoffield(elapsed_frame):
    p0 = [125, 340]
    p1 = [ 77, 291]
    p2 = [ 29, 288]
    p3 = [ 15, 334]
    
    t = elapsed_frame / (g.FPS * 0.25)
    t2 = clamp(t, 0, 1)
    
    x, y = bezier(*p0, *p1, *p2, *p3, t2)
    
    return x, y, t2

# return
#   x, y    発射物の座標
#   t       発射物の時刻（0 ~ 1.0)   
def calc_projectile(proj, current_frame):

    elapsed_frame = current_frame - proj.start_frame
    
    if (proj.move_type == MoveType.Normal):
        x, y, t = move_normal(elapsed_frame)
    elif (proj.move_type == MoveType.Yamanari):
        x, y, t = move_yamanari(elapsed_frame)
    elif (proj.move_type == MoveType.OutField):
        x, y, t = move_outoffield(elapsed_frame)
    
    return x, y, t

def draw_projectile(surface, proj, current_frame):

    x, y, t = calc_projectile(proj, current_frame)
    
    if (proj.projectile_type == ProjectileType.Egg):
        img_src = g.img_projectile_list[0]
        img_src = pygame.transform.rotate(img_src, t * 90 + proj.rotate)
    elif (proj.projectile_type == ProjectileType.Bomb):
        img_src = g.img_projectile_list[1]
    
    surface.blit(img_src, (x - img_src.get_width() * 0.5, y - img_src.get_height() * 0.5))

def draw_player(surface, game_state, player_state, elapsed_frame):
    
    ofs_x, ofs_y = 0, 0
    
    if (player_state == PlayerState.Eat):
        img_no = 0
        if (game_state == Game.State.MAINGAME and elapsed_frame <= 8): ofs_x = math.cos(elapsed_frame * math.pi * 0.5) * 4
    elif (player_state == PlayerState.Guard):
        img_no = 1
        if (game_state == Game.State.MAINGAME and elapsed_frame <= 3): ofs_y = math.cos((3 - elapsed_frame) / 3 * (math.pi * 0.5)) * 5
    else: # PlayerState.Damage, PlayerState.Dead
        img_no = 2
    
    img_player = g.img_player_list[img_no]
    surface.blit(img_player, (86 + ofs_x, 320 + ofs_y))
    
    # プレイヤー失敗時の爆発
    if (player_state == PlayerState.Damage): 
        l = [
            [[-64,  0, 1], [0, 0, 0], [64,  0, 1]],
            [[  0,-64, 0], [0, 0, 1], [ 0, 64, 0]],
            [[  0,-64, 1], [0, 0, 0], [ 0, 64, 1]],
            [[-64,  0, 0], [0, 0, 1], [64,  0, 0]],
            [[0, 0, 0]],
        ]
        
        index = int(elapsed_frame * 0.5)
        
        if (index < len(l)):
            for ofs_x, ofs_y, img_no in l[index]:
                surface.blit(g.img_explode_list[img_no], (94 + ofs_x, 320 + ofs_y))

def draw_pitcher(surface, elapsed_frame):

    ofs_x, ofs_y = 0, 0
    
    if (elapsed_frame <= 2):
        img_pitch = g.img_pitcher_list[1]
    elif (elapsed_frame <= 4):
        img_pitch = g.img_pitcher_list[0]
        ofs_x = -35
    elif (elapsed_frame <= 6):
        img_pitch = g.img_pitcher_list[2]
        ofs_x = -15
        ofs_y = 20
    else:
        img_pitch = g.img_pitcher_list[3]
    
    surface.blit(img_pitch, (430 + ofs_x, 172 + ofs_y))


def load_image():

    folder = 'image/'
    
    # プレイヤーキャラクタ
    img_src = pygame.image.load(f'{folder}player.png').convert_alpha()
    tmp_list = []

    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (0, 0, 64, 64))
    tmp_list.append(surface)

    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (64, 0, 64, 64))
    tmp_list.append(surface)

    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (128, 0, 64, 64))
    tmp_list.append(surface)

    g.img_player_list = tmp_list

    # タマゴ、ボム
    img_src = pygame.image.load(f'{folder}object.png').convert_alpha()
    tmp_list = []

    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (0, 0, 40, 40))
    tmp_list.append(surface)

    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (40, 0, 40, 40))
    tmp_list.append(surface)

    g.img_projectile_list = tmp_list

    # 爆発
    img_src = pygame.image.load(f'{folder}explode.png').convert_alpha()
    tmp_list = []

    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (0, 0, 64, 64))
    tmp_list.append(surface) 
    
    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (64, 0, 64, 64))
    tmp_list.append(surface)

    g.img_explode_list = tmp_list

    # ピッチャー
    img_src = pygame.image.load(f'{folder}pitcher.png').convert_alpha()
    tmp_list = []

    surface = pygame.Surface((128, 128), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (0, 0, 128, 128))
    tmp_list.append(surface)
    
    surface = pygame.Surface((128, 128), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (128, 0, 128, 128))
    tmp_list.append(surface)

    surface = pygame.Surface((128, 128), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (0, 128, 128, 128))
    tmp_list.append(surface)

    surface = pygame.Surface((128, 128), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (128, 128, 128, 128))
    tmp_list.append(surface)

    g.img_pitcher_list = tmp_list

    img_src = pygame.image.load(f'{folder}score.png').convert_alpha()
    tmp_list = []

    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (0, 0, 16, 16))
    tmp_list.append(surface)
    
    surface = pygame.Surface((64, 64), flags=pygame.SRCALPHA)
    surface.blit(img_src, (0, 0), (16, 0, 16, 16))
    tmp_list.append(surface)
    
    g.img_score_list = tmp_list

    # 背景
    g.img_background = pygame.image.load(f'{folder}background.png').convert_alpha()

def load_sound():

    folder = 'sound/'
    
    g.snd_swing = pygame.mixer.Sound(f'{folder}swing25_c.wav')
    g.snd_eat = pygame.mixer.Sound(f'{folder}puu77_b.wav')
    g.snd_guard = pygame.mixer.Sound(f'{folder}bosu20.wav')
    g.snd_exlode = pygame.mixer.Sound(f'{folder}gun08.wav')
    g.bgm_battle  = pygame.mixer.Sound(f'{folder}Isogriv.mp3')
    g.bgm_fanfare = pygame.mixer.Sound(f'{folder}mini_fanfare.mp3')
    
    scale = 0.2

    g.snd_swing.set_volume(0.5 * scale)
    g.snd_eat.set_volume(0.70 * scale)
    g.snd_guard.set_volume(0.5 * scale)
    g.snd_exlode.set_volume(0.5 * scale)
    g.bgm_battle.set_volume(0.5 * scale) 
    g.bgm_fanfare.set_volume(0.5 * scale)


def play_bgm(bgm):

    if (g.current_bgm != None):
        g.current_bgm.stop()
    
    g.current_bgm = bgm
    g.current_bgm.play()

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
        self.player_state = PlayerState.Eat
        self.player_frame = -99999
        self.pitcher_frame = -99999  # ピッチャーが最後に投球した時刻（フレーム）
        self.score = 0
    
    def start_menu(self):
        self.game_state = self.State.START
        self.game_state_frame = 0
    
    def maingame(self):
        self.game_state = self.State.MAINGAME
        self.game_state_frame = 0
        
        play_bgm(g.bgm_battle)
        
        self.reset()
    
    def result(self):
        self.game_state = self.State.RESULT
        self.game_state_frame = 0

        play_bgm(g.bgm_fanfare)
    
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

        self.update_player()

        # 発射物の更新
        for p in self.projectile_list[:]: # スナップショットを取る
        
            x, y, t = calc_projectile(p, self.game_state_frame)
            
            if (t < 1.0): continue # まだ終点に届いていない
            
            if (MoveType.in_field(p.move_type)):
            
                if (self.player_state == PlayerState.Guard):
                    # 弾をガードした
                    self.player_frame = self.game_state_frame

                    self.projectile_list.append(\
                        Projectile(p.projectile_type, self.game_state_frame, MoveType.OutField))
                    
                    g.snd_guard.play()

                elif (self.player_state == PlayerState.Eat):
                    # 卵ならスコア加算
                    if (p.projectile_type == ProjectileType.Egg):
                        self.player_frame = self.game_state_frame
                        self.score += 1
                        g.snd_eat.play()
                    
                    elif (p.projectile_type == ProjectileType.Bomb):
                        # 爆弾をたべたら失敗！
                        self.failed()
                        g.snd_exlode.play()

                        self.player_state = PlayerState.Damage
                        self.player_frame = 0
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

                # 発射物をワールドに追加
                self.projectile_list.append(\
                    Projectile(event.projectile_type, self.game_state_frame, event.move_type))
                
                self.pitcher_frame = self.game_state_frame
                g.snd_swing.play()

            else: # イベントの発生なし
                break

    def update_result(self):
        if (1.0 * g.FPS <= self.game_state_frame):
            self.retry_menu()

    def update_failed(self):
        if (1.0 * g.FPS <= self.game_state_frame):
            self.result()
            self.player_state = PlayerState.Dead
            self.player_frame = 0

    def update_retry(self):
    
        pressed = pygame.key.get_pressed()
        
        if pressed[pygame.K_SPACE]:
            self.maingame()
    
    def update_player(self):
    
        pressed = pygame.key.get_pressed()
        
        if pressed[pygame.K_DOWN]:
            self.player_state = PlayerState.Guard
        else:
            self.player_state = PlayerState.Eat
    
    def render(self, surface):
    
        # 背景の描画
        surface.blit(g.img_background, (0, 0))

        # プレイヤーの描画
        draw_player(surface, self.game_state, self.player_state, self.game_state_frame - self.player_frame)
        
        # ピッチャーの描画
        draw_pitcher(surface,
            self.game_state_frame - self.pitcher_frame if (self.game_state == self.State.MAINGAME) else 99999)

        # スコアの描画
        for i in range(30):
            x = int(i / 10)
            y = (i % 10)
            img = g.img_score_list[1 if i < self.score else 0]
            
            surface.blit(img, (100 + x * -24, 240 + y * -24))
        
        # 卵や爆弾オブジェの描画
        for proj in self.projectile_list:
            draw_projectile(surface, proj, self.game_state_frame)

        # 各ゲームシーケンスの描画
        if (self.game_state == self.State.START):
            draw_text(surface, "スペースキーを押したら開始！", (0, 0, 0), (160 + 1, 420 + 1))
            draw_text(surface, "スペースキーを押したら開始！", (255, 128, 128), (160, 420))
        elif (self.game_state == self.State.FAILED):
            draw_text(surface, "失敗・・・！", (0, 0, 0), (160 + 1, 420 + 1))
            draw_text(surface, "失敗・・・！", (128, 96, 64), (160, 420))
        elif (self.game_state == self.State.RESULT):
            draw_text(surface, f"結果表示 スコア:{self.score}", (0, 0, 0), (160 + 1, 420 + 1))
            draw_text(surface, f"結果表示 スコア:{self.score}", (128, 96, 64), (160, 420))
        elif (self.game_state == self.State.RETRY):
            draw_text(surface, "スペースキーでリトライ", (0, 0, 0), (160 + 1, 420 + 1))
            draw_text(surface, "スペースキーでリトライ", (128, 96, 64), (160, 420))


def main():
    
    # システムの初期化
    pygame.init()
    window = pygame.display.set_mode((g.WINDOW_WIDTH, g.WINDOW_HEIGHT))
    g.font = pygame.font.Font("C:\Windows\Fonts\meiryo.ttc", 20)

    load_image()
    load_sound()
    
    clock = pygame.time.Clock()
    
    # ゲームの作成
    game = Game()

    while True:
    
        window.fill((0, 0, 255))
        
        game.update()
        game.render(window)
        
        # FPSの描画
        draw_text(window, str(round(clock.get_fps(), 2)), (255, 255, 255), (580, 0))

        pygame.display.update()
        
        clock.tick(g.FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

if __name__ == '__main__':
    main()
