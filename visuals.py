import pygame

BG_COLOR = (18, 18, 24)
DEFAULT_COLOR = (90, 110, 200)
ACTIVE_COLOR = (240, 200, 60)
FINALIZED_COLOR = (80, 200, 120)


def draw_bars(screen, arr, active_indices, finalized, margin=20):
    width, height = screen.get_size()
    screen.fill(BG_COLOR)

    n = len(arr)
    if n == 0:
        return

    plot_w = width - 2 * margin
    plot_h = height - 2 * margin
    bar_w = plot_w / n
    max_val = max(arr)

    for i, val in enumerate(arr):
        bar_h = (val / max_val) * plot_h if max_val else 0
        x = margin + i * bar_w
        y = height - margin - bar_h

        if finalized:
            color = FINALIZED_COLOR
        elif i in active_indices:
            color = ACTIVE_COLOR
        else:
            color = DEFAULT_COLOR

        pygame.draw.rect(screen, color, (x, y, max(bar_w - 1, 1), bar_h))
