import pygame
import numpy as np

# Init Pygame
pygame.mixer.pre_init(channels=1, allowedchanges=0, buffer=2048)
pygame.init()
pygame.mixer.set_num_channels(24)
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Window setup
width, height = 1600, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Visual Notes")

# Base frequencies (adjust keys for different keyboards)
base_frequencies = {
    pygame.K_CAPSLOCK: 246.94,  # B3
    pygame.K_a: 261.63,  # C4
    pygame.K_w: 277.18,  # C4#
    pygame.K_s: 293.66,  # D4
    pygame.K_e: 311.13,  # D4#
    pygame.K_d: 329.63,  # E4
    pygame.K_f: 349.23,  # F4
    pygame.K_t: 370.00,  # F4#
    pygame.K_g: 392.00,  # G4
    pygame.K_z: 415.30,  # G4#
    pygame.K_h: 440.00,  # A4
    pygame.K_u: 466.16,  # A4#
    pygame.K_j: 493.88,  # B4
    pygame.K_k: 523.25,  # C5
    pygame.K_o: 554.37,  # C5#
    pygame.K_l: 587.33,  # D5
    pygame.K_p: 622.25,  # D5#
    pygame.key.key_code("ö"): 659.25,  # E5
    pygame.key.key_code("ä"): 698.46,  # F5
    pygame.K_HASH: 783.99,   # G5
    pygame.K_RETURN: 880.00   # A5
}

# Variables
sample_rate = 44100
visual_timescale = 0.04
octave_shift = 0
amplitude_factor = 1.0
tones = {}
pressed_keys = set()
playing_channels = {}

# Generate tones based on current octave
def generate_tones():
    global tones
    for key, base_freq in base_frequencies.items():
        freq = base_freq * (2 ** octave_shift)
        k = round(freq)
        N = int((k / freq) * sample_rate)
        t = np.arange(N) / sample_rate
        tone = np.sin(2 * np.pi * freq * t)
        tones[key] = pygame.sndarray.make_sound((tone * 2000).astype(np.int16))

# Initial tones
generate_tones()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in base_frequencies and event.key not in pressed_keys:
                pressed_keys.add(event.key)
                channel = tones[event.key].play(-1)
                channel.set_volume(amplitude_factor)
                playing_channels[event.key] = channel
            elif event.key == pygame.K_UP:
                amplitude_factor = min(1.0, amplitude_factor + 0.1)
                for key in pressed_keys:
                    playing_channels[key].set_volume(amplitude_factor)
            elif event.key == pygame.K_DOWN:
                amplitude_factor = max(0.1, amplitude_factor - 0.1)
                for key in pressed_keys:
                    playing_channels[key].set_volume(amplitude_factor)
            elif event.key == pygame.K_RIGHT:
                octave_shift += 1
                generate_tones()
                for key in pressed_keys:
                    playing_channels[key].stop()
                    channel = tones[key].play(-1)
                    channel.set_volume(amplitude_factor)
                    playing_channels[key] = channel
            elif event.key == pygame.K_LEFT:
                octave_shift -= 1
                generate_tones()
                for key in pressed_keys:
                    playing_channels[key].stop()
                    channel = tones[key].play(-1)
                    channel.set_volume(amplitude_factor)
                    playing_channels[key] = channel
        elif event.type == pygame.KEYUP:
            if event.key in base_frequencies and event.key in pressed_keys:
                pressed_keys.remove(event.key)
                playing_channels[event.key].stop()
                del playing_channels[event.key]
        elif event.type == pygame.MOUSEWHEEL:
            visual_timescale = max(0.01, min(0.2, visual_timescale - event.y * 0.005))

    # Draw
    screen.fill((0, 0, 0))
    if pressed_keys:
        freq_text = ""
        x = np.arange(width)
        combined_wave = np.zeros_like(x, dtype=float)
        base_freqs = {base_frequencies[key] for key in pressed_keys}
        for base_freq in base_freqs:
            freq = base_freq * (2 ** octave_shift)
            freq_text += str(freq) + " Hz \n"
            combined_wave += np.sin(2 * np.pi * freq * (x / width * visual_timescale))
        y_display = (100 * amplitude_factor) * combined_wave + height // 2
        points = [(i, int(y)) for i, y in enumerate(y_display) if 0 <= y < height]
        if points:
            pygame.draw.lines(screen, (255, 0, 0), False, points, 2)
        if freq_text != "":
            text = font.render(freq_text, True, (255, 255, 255))
            screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
