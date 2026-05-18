import pygame
import random
import sys
from bfs import BFS

# ── Cấu hình gốc (resizable: tính lại mỗi frame) ───────────────────────────
BASE_WIDTH,  BASE_HEIGHT = 820, 520
MIN_WIDTH,   MIN_HEIGHT  = 600, 420
TILE = 120          # kích thước ô (sẽ scale theo width)
GAP  = 6

# Màu sắc
BG_COLOR      = (15,  20,  40)
PANEL_COLOR   = (25,  32,  60)
TILE_COLOR    = (60,  120, 220)
TILE_EMPTY    = (20,  28,  55)
TILE_CORRECT  = (40,  200, 120)
TILE_HOVER    = (90,  160, 255)
TEXT_COLOR    = (240, 245, 255)
LABEL_COLOR   = (160, 180, 220)
HINT_BTN_CLR  = (220, 80,  60)
HINT_BTN_HOV  = (255, 110, 90)
HINT_TEXT_CLR = (255, 230, 100)
SHADOW        = (10,  14,  30)

# ── Helper ──────────────────────────────────────────────────────────────────

def calc_layout(w, h):
    """
    Tính toán layout động theo kích thước cửa sổ.
    Trả về dict chứa mọi tham số vị trí / kích thước.
    """
    # tile scale theo chiều rộng, giới hạn 80..160
    tile = max(80, min(160, (w - 120) // 8))
    gap  = max(4, tile // 20)

    board_px = 3 * tile + 2 * gap          # chiều rộng/cao 1 bảng
    padding  = max(30, (w - 2 * board_px) // 3)   # lề 2 bên + khoảng giữa

    # Panel background cho mỗi bảng (thêm 20px mỗi phía)
    panel_pad = 18
    panel_w   = board_px + panel_pad * 2
    panel_h   = board_px + panel_pad * 2 + 34  # + chỗ label phía trên

    left_panel_x  = padding
    right_panel_x = w - padding - panel_w

    board_offset_y = max(80, h // 5)

    hint_btn_w = 200
    hint_btn_h = 44
    hint_btn = pygame.Rect(
        w // 2 - hint_btn_w // 2,
        h - 70,
        hint_btn_w, hint_btn_h
    )

    return dict(
        tile=tile, gap=gap, board_px=board_px,
        panel_pad=panel_pad, panel_w=panel_w, panel_h=panel_h,
        left_panel_x=left_panel_x,   right_panel_x=right_panel_x,
        left_board_x=left_panel_x  + panel_pad,
        right_board_x=right_panel_x + panel_pad,
        board_offset_y=board_offset_y,
        hint_btn=hint_btn,
        divider_x=w // 2,
    )

def draw_panel(surface, lx, ly, pw, ph, tile):
    """Vẽ nền panel bo góc với đường viền mờ."""
    r = pygame.Rect(lx, ly, pw, ph)
    pygame.draw.rect(surface, PANEL_COLOR, r, border_radius=16)
    pygame.draw.rect(surface, (50, 65, 110), r, width=2, border_radius=16)

def draw_tile(surface, num, rect, color, font):
    shadow_rect = rect.move(3, 3)
    pygame.draw.rect(surface, SHADOW, shadow_rect, border_radius=12)
    pygame.draw.rect(surface, color, rect, border_radius=12)
    if num != 0:
        txt = font.render(str(num), True, TEXT_COLOR)
        surface.blit(txt, txt.get_rect(center=rect.center))

def draw_board(surface, board, origin_x, origin_y, tile, gap, font,
               highlight=None, reference=None):
    """Vẽ một bảng 3x3 với tile/gap động."""
    for row in range(3):
        for col in range(3):
            num = board[row * 3 + col]
            rect = pygame.Rect(
                origin_x + col * (tile + gap),
                origin_y + row * (tile + gap),
                tile, tile
            )
            if num == 0:
                color = TILE_EMPTY
            elif reference and reference[row * 3 + col] == num:
                color = TILE_CORRECT
            elif highlight and (col, row) in highlight:
                color = TILE_HOVER
            else:
                color = TILE_COLOR
            draw_tile(surface, num, rect, color, font)

def find_blank(board):
    return board.index(0)

def is_solvable(board) -> bool:
    flat = [x for x in board if x != 0]
    inv = sum(1 for i in range(len(flat))
              for j in range(i+1, len(flat)) if flat[i] > flat[j])
    return inv % 2 == 0

def random_board() -> list:
    b = list(range(9))
    while True:
        random.shuffle(b)
        if is_solvable(b) and b != list(range(9)):
            return b

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    pygame.init()

    # ★ RESIZABLE: thêm flag pygame.RESIZABLE
    screen = pygame.display.set_mode(
        (BASE_WIDTH, BASE_HEIGHT),
        pygame.RESIZABLE          # ← cho phép kéo góc cửa sổ
    )
    pygame.display.set_caption("8-Puzzle")
    clock = pygame.time.Clock()

    font_big  = pygame.font.SysFont("segoeui", 48, bold=True)
    font_sm   = pygame.font.SysFont("segoeui", 20)
    font_hint = pygame.font.SysFont("segoeui", 18)

    target_board = list(range(1, 9)) + [0]
    player_board = random_board()
    hint_steps   = []
    hint_index   = 0
    hint_msg     = ""
    hover_tiles  = set()
    won          = False

    def try_move_tile(mx, my):
        nonlocal player_board
        nonlocal won
        nonlocal hint_steps
        nonlocal hint_index
        nonlocal hint_msg

        if won:
            return

        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:

            nr = br + dr
            nc = bc + dc

            if not (0 <= nr < 3 and 0 <= nc < 3):
                continue

            rx = L['right_board_x'] + nc * (tile + gap)
            ry = L['board_offset_y'] + nr * (tile + gap)

            rect = pygame.Rect(rx, ry, tile, tile)

            if rect.collidepoint(mx, my):

                ni = nr * 3 + nc

                player_board[blank], player_board[ni] = \
                    player_board[ni], player_board[blank]

                hint_steps.clear()

                hint_index = 0

                hint_msg = ""

                if player_board == target_board:
                    won = True

                return

    def handle_hint() -> str:
        nonlocal player_board
        nonlocal hint_steps
        nonlocal hint_index
        nonlocal hint_msg
        nonlocal won

        if won or player_board == target_board:
            return "Da giai xong roi, nhan R de choi lai"
        

        if not hint_steps:
            hint_steps = BFS(player_board, target_board)
            hint_index = 0

        message = f"Di chuyen: {hint_steps[hint_index]}"
        hint_index += 1

        return message

    def reset():
        nonlocal player_board, hint_steps, hint_index, hint_msg, won
        player_board = random_board()
        hint_steps = []; hint_index = 0; hint_msg = ""; won = False

    # ── Game loop ──────────────────────────────────────────────────────────
    while True:
        # Lấy kích thước cửa sổ hiện tại (thay đổi khi người dùng kéo)
        W, H = screen.get_size()

        # Giữ kích thước tối thiểu (pygame không enforce natively)
        if W < MIN_WIDTH or H < MIN_HEIGHT:
            W = max(W, MIN_WIDTH)
            H = max(H, MIN_HEIGHT)
            screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)

        # Tính lại layout theo kích thước mới
        L = calc_layout(W, H)
        tile = L['tile']; gap = L['gap']

        # Font tile scale theo tile size
        fs = max(16, tile // 4)
        font_tile = pygame.font.SysFont("segoeui", fs, bold=True)

        mx, my = pygame.mouse.get_pos()

        # ── Hover detection (bảng player) ──
        hover_tiles = set()
        blank = find_blank(player_board)
        br, bc = divmod(blank, 3)
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = br+dr, bc+dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                rx = L['right_board_x'] + nc*(tile+gap)
                ry = L['board_offset_y'] + nr*(tile+gap)
                if pygame.Rect(rx, ry, tile, tile).collidepoint(mx, my):
                    hover_tiles.add((nc, nr))

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ★ VIDEORESIZE: pygame bắn event này khi cửa sổ thay đổi kích thước
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (max(event.w, MIN_WIDTH), max(event.h, MIN_HEIGHT)),
                    pygame.RESIZABLE
                )

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                try_move_tile(mx, my)

                if L['hint_btn'].collidepoint(mx, my):
                    hint_msg = handle_hint()

        # ── Draw ───────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)

        # ── Panel trái (TARGET) ──
        panel_y = L['board_offset_y'] - L['panel_pad'] - 30
        draw_panel(screen,
                   L['left_panel_x'], panel_y,
                   L['panel_w'], L['panel_h'], tile)

        lbl_t = font_sm.render("🎯  TARGET", True, LABEL_COLOR)
        screen.blit(lbl_t, (L['left_board_x'], L['board_offset_y'] - 26))

        draw_board(screen, target_board,
                   L['left_board_x'], L['board_offset_y'],
                   tile, gap, font_tile)

        # ── Divider dọc giữa 2 panel ──
        div_x = W // 2
        pygame.draw.line(screen, (40, 55, 90),
                         (div_x, 70), (div_x, H - 80), 2)

        # ── Panel phải (PLAYER) ──
        draw_panel(screen,
                   L['right_panel_x'], panel_y,
                   L['panel_w'], L['panel_h'], tile)

        lbl_p = font_sm.render("🕹  PLAYER  (click để di chuyển)", True, LABEL_COLOR)
        screen.blit(lbl_p, (L['right_board_x'], L['board_offset_y'] - 26))

        draw_board(screen, player_board,
                   L['right_board_x'], L['board_offset_y'],
                   tile, gap, font_tile,
                   highlight=hover_tiles,
                   reference=target_board if not won else None)

        # ── Nút Hint ──
        hbtn = L['hint_btn']
        btn_color = HINT_BTN_HOV if hbtn.collidepoint(mx, my) else HINT_BTN_CLR
        pygame.draw.rect(screen, btn_color, hbtn, border_radius=10)
        btn_lbl = "💡 HINT (tiếp theo)" if hint_steps else "💡 HINT"
        btn_txt = font_sm.render(btn_lbl, True, TEXT_COLOR)
        screen.blit(btn_txt, btn_txt.get_rect(center=hbtn.center))

        if hint_msg:
            msg_surf = font_hint.render(hint_msg, True, HINT_TEXT_CLR)
            screen.blit(msg_surf, msg_surf.get_rect(centerx=W//2, y=H - 105))

        # ── Thắng overlay ──
        if won:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            win_txt = font_big.render("🎉  BẠN ĐÃ GIẢI XONG!", True, (255, 220, 50))
            screen.blit(win_txt, win_txt.get_rect(center=(W//2, H//2 - 24)))
            sub_txt = font_sm.render("Nhấn  R  để chơi lại", True, TEXT_COLOR)
            screen.blit(sub_txt, sub_txt.get_rect(center=(W//2, H//2 + 36)))

        key_hint = font_hint.render("R = chơi lại", True, (70, 90, 130))
        screen.blit(key_hint, (8, H - 22))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()