from threading import Thread
import pygame
import atexit
import os
from tts import TTS

# TODO: Either clean this up or rewrite it in something else

class Dougterface:
    def __init__(self, tts: TTS, width=800, height=600):
        self.tts = tts
        self.width = width
        self.height = height
        self.running = False
        self.thread = None
        self._cached_text = None
        self._cached_surface = None
        atexit.register(self.stop)

    def wrap_text(self, text, font, max_width):
        lines, current = [], ""
        for word in text.split():
            if font.size(current + word + " ")[0] <= max_width:
                current += word + " "
            else:
                lines.append(current)
                current = word + " "
        lines.append(current)
        return lines

    def render_text_surface(self, text, font, max_width):
        lines = self.wrap_text(text, font, max_width)
        surface = pygame.Surface((self.width, len(lines) * font.get_linesize()), pygame.SRCALPHA)
        WHITE, BLACK = (255, 255, 255), (0, 0, 0)
        for i, line in enumerate(lines):
            y = i * font.get_linesize() + font.get_linesize() // 2
            outline = font.render(line, True, BLACK)
            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]:
                rect = outline.get_rect(center=(self.width//2 + dx, y + dy))
                surface.blit(outline, rect)
            main = font.render(line, True, WHITE)
            surface.blit(main, main.get_rect(center=(self.width//2, y)))
        return surface

    def start(self):
        if self.running: return
        self.running = True

        def run():
            pygame.init()
            screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("The Douglang Dougterface")
            font = pygame.font.Font(None, 50)
            clock = pygame.time.Clock()
            BG = (100, 100, 100)

            sprite_path = os.path.join(os.path.dirname(__file__), "assets/wario_pepper.png")
            sprite = pygame.transform.smoothscale(
                pygame.image.load(sprite_path).convert_alpha(), (522//3, 578//3)
            )

            while self.running:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        self.running = False

                # Update text if changed
                text = self.tts.current_text
                if text != self._cached_text:
                    self._cached_surface = self.render_text_surface(text, font, self.width - 40)
                    self._cached_text = text

                screen.fill(BG)

                # Determine resting positions (no amplitude offset)
                text_height = self._cached_surface.get_height() if self._cached_surface else 0
                sprite_height = sprite.get_height()
                total_height = sprite_height + text_height
                block_top = (self.height - total_height) // 2 # vertical center of combined block

                # Draw sprite with amplitude effects on top of centered resting position
                amplitude = self.tts.get_amplitude()
                rotated_sprite = pygame.transform.rotozoom(sprite, -amplitude*30, 1.0)
                sprite_rect = rotated_sprite.get_rect()
                sprite_rect.centerx = self.width // 2
                # Resting bottom aligned with top of text, then apply amplitude vertical offset
                sprite_rect.bottom = block_top + sprite_height + (-amplitude * 20)
                screen.blit(rotated_sprite, sprite_rect)

                # Draw text directly below sprite (resting position)
                if self._cached_surface:
                    text_y = block_top + sprite_height
                    screen.blit(self._cached_surface, (0, text_y))

                pygame.display.flip()
                clock.tick(60)

            pygame.quit()

        self.thread = Thread(target=run, daemon=True)
        self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join()