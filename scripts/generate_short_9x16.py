"""
Automated 9:16 Vertical Short/Reel Generator for Lumina Dental Studio
Generates a high-definition 1080x1920 vertical promotional video (MP4)
from clinic assets with Ken Burns 3D camera pan/zoom, cross-dissolves,
clinical typography overlays, and soothing ambient synthetic audio track (AAC).
Strictly optimized for Instagram Reels, YouTube Shorts, and Facebook Reels (< 8 MB).
"""

import os
import sys
import subprocess
import wave

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "frontend", "public", "social-kit")
OUTPUT_VIDEO = os.path.join(ASSETS_DIR, "lumina-short-9x16.mp4")
TEMP_AUDIO = os.path.join(ASSETS_DIR, "temp_ambient_short.wav")

# Video Settings (9:16 Vertical HD)
WIDTH = 1080
HEIGHT = 1920
FPS = 30
SCENE_DURATION_SEC = 3.2
FADE_DURATION_SEC = 0.5
TOTAL_SCENES = 5

# Typography
FONT_BOLD_PATH = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR_PATH = "C:/Windows/Fonts/segoeui.ttf"

try:
    FONT_BADGE = ImageFont.truetype(FONT_BOLD_PATH, 28)
    FONT_TITLE = ImageFont.truetype(FONT_BOLD_PATH, 58)
    FONT_SUBTITLE = ImageFont.truetype(FONT_REGULAR_PATH, 32)
except Exception:
    FONT_BADGE = ImageFont.load_default()
    FONT_TITLE = ImageFont.load_default()
    FONT_SUBTITLE = ImageFont.load_default()

# Chromatic Tokens
COLOR_NAVY_BG = (5, 19, 32)            # #051320
COLOR_CYAN_ACCENT = (0, 229, 255)       # #00E5FF
COLOR_WHITE = (255, 255, 255)           # Diamond White
COLOR_SILVER = (148, 163, 184)          # Titanium Silver

# Scene definitions
SCENES = [
    {
        "image": "lumina-logo.png",
        "badge": "✦ LUMINA DENTAL STUDIO",
        "title": "Odontología de Precisión",
        "subtitle": "Atención 24/7 con IA • Reserva en Segundos",
        "zoom_start": 1.00,
        "zoom_end": 1.15,
        "pan_x": 0.0,
        "pan_y": 0.0
    },
    {
        "image": "lumina-cover.png",
        "badge": "✦ CLÍNICA & TECNOLOGÍA DIGITAL",
        "title": "Diseño y Escaneo 3D",
        "subtitle": "Infraestructura médica de última generación",
        "zoom_start": 1.05,
        "zoom_end": 1.20,
        "pan_x": -0.04,
        "pan_y": 0.02
    },
    {
        "image": "ig-post-blanqueamiento.png",
        "badge": "✦ ESTÉTICA CLÍNICA • $90 A $150 USD",
        "title": "Blanqueamiento Láser",
        "subtitle": "Sonrisa radiante en 1 sola sesión de 45 min",
        "zoom_start": 1.00,
        "zoom_end": 1.12,
        "pan_x": 0.02,
        "pan_y": -0.02
    },
    {
        "image": "ig-post-implantes.png",
        "badge": "✦ CIRUGÍA DIGITAL • $350 A $600 USD",
        "title": "Implantes Guiados 3D",
        "subtitle": "Fijación milimétrica en titanio y zafiro",
        "zoom_start": 1.02,
        "zoom_end": 1.15,
        "pan_x": -0.03,
        "pan_y": 0.02
    },
    {
        "image": "ig-post-urgencias.png",
        "badge": "✦ GUARDIA & TRIAGE 24/7 • INMEDIATO",
        "title": "Urgencias Odontológicas",
        "subtitle": "Alivio del dolor inmediato • Agenda WhatsApp",
        "zoom_start": 1.00,
        "zoom_end": 1.14,
        "pan_x": 0.01,
        "pan_y": 0.02
    }
]

def generate_ambient_audio(duration_sec, output_wav):
    """
    Synthesizes a peaceful ambient clinic soundtrack (A maj7 healing chord pad)
    """
    rate = 44100
    total_samples = int(duration_sec * rate)
    t = np.linspace(0, duration_sec, total_samples, endpoint=False)
    
    # Chord frequencies: A2 (110Hz), E3 (164.81Hz), G#3 (207.65Hz), C#4 (277.18Hz), E4 (329.63Hz)
    freqs = [110.0, 164.81, 207.65, 277.18, 329.63]
    audio = np.zeros(total_samples, dtype=np.float32)
    
    for f in freqs:
        # Subtle harmonic shimmer
        audio += 0.20 * np.sin(2 * np.pi * f * t)
        audio += 0.05 * np.sin(2 * np.pi * (f * 2) * t)
    
    # 0.2Hz gentle binaural swell
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * 0.2 * t)
    audio = audio * swell
    
    # Normalize
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.70
    
    # Smooth fade-in (1.5s) and fade-out (1.5s)
    fade_in = np.clip(t / 1.5, 0.0, 1.0)
    fade_out = np.clip((duration_sec - t) / 1.5, 0.0, 1.0)
    audio = audio * fade_in * fade_out
    
    # Convert to 16-bit PCM stereo
    audio_int16 = (audio * 32767).astype(np.int16)
    stereo = np.column_stack((audio_int16, audio_int16))
    
    with wave.open(output_wav, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(stereo.tobytes())
        
    print(f"Generated synthetic ambient audio track for Short: {output_wav}")

def load_and_prepare_image(filename):
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing asset image: {path}")
    
    img = Image.open(path).convert("RGBA")
    
    # For vertical 9:16 (1080x1920), create canvas with zoom safety
    canvas_w = int(WIDTH * 1.35)
    canvas_h = int(HEIGHT * 1.35)
    
    # Scale to fill canvas completely
    ratio = max(canvas_w / img.width, canvas_h / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - canvas_w) // 2
    top = (new_h - canvas_h) // 2
    img_cropped = img_resized.crop((left, top, left + canvas_w, top + canvas_h))
    return img_cropped

def render_overlay(frame_img, scene_data, t):
    """
    Renders glassmorphic typography overlay scaled for vertical 9:16 mobile format
    """
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    alpha_factor = min(1.0, t * 2.5)
    
    # Lower third glassmorphism card (safe zone for mobile reels/shorts)
    card_x0 = 70
    card_x1 = WIDTH - 70
    card_y0 = HEIGHT - 460
    card_y1 = HEIGHT - 180
    radius = 32
    
    # Dark Abyssal Navy glass box
    draw.rounded_rectangle(
        [(card_x0, card_y0), (card_x1, card_y1)],
        radius=radius,
        fill=(COLOR_NAVY_BG[0], COLOR_NAVY_BG[1], COLOR_NAVY_BG[2], int(220 * alpha_factor)),
        outline=(COLOR_CYAN_ACCENT[0], COLOR_CYAN_ACCENT[1], COLOR_CYAN_ACCENT[2], int(180 * alpha_factor)),
        width=2
    )
    
    # Cyan accent pill badge
    badge_text = scene_data["badge"]
    badge_bg = (COLOR_CYAN_ACCENT[0], COLOR_CYAN_ACCENT[1], COLOR_CYAN_ACCENT[2], int(40 * alpha_factor))
    badge_border = (COLOR_CYAN_ACCENT[0], COLOR_CYAN_ACCENT[1], COLOR_CYAN_ACCENT[2], int(180 * alpha_factor))
    
    draw.rounded_rectangle(
        [(card_x0 + 36, card_y0 + 30), (card_x0 + 580, card_y0 + 76)],
        radius=14,
        fill=badge_bg,
        outline=badge_border,
        width=1
    )
    
    draw.text(
        (card_x0 + 54, card_y0 + 36),
        badge_text,
        font=FONT_BADGE,
        fill=(COLOR_CYAN_ACCENT[0], COLOR_CYAN_ACCENT[1], COLOR_CYAN_ACCENT[2], int(255 * alpha_factor))
    )
    
    # Main Title
    draw.text(
        (card_x0 + 36, card_y0 + 94),
        scene_data["title"],
        font=FONT_TITLE,
        fill=(COLOR_WHITE[0], COLOR_WHITE[1], COLOR_WHITE[2], int(255 * alpha_factor))
    )
    
    # Neon cyan divider line
    draw.line(
        [(card_x0 + 36, card_y0 + 180), (card_x1 - 36, card_y0 + 180)],
        fill=(COLOR_CYAN_ACCENT[0], COLOR_CYAN_ACCENT[1], COLOR_CYAN_ACCENT[2], int(90 * alpha_factor)),
        width=1
    )
    
    # Subtitle
    draw.text(
        (card_x0 + 36, card_y0 + 198),
        scene_data["subtitle"],
        font=FONT_SUBTITLE,
        fill=(COLOR_SILVER[0], COLOR_SILVER[1], COLOR_SILVER[2], int(240 * alpha_factor))
    )
    
    return Image.alpha_composite(frame_img.convert("RGBA"), overlay).convert("RGB")

def get_scene_frame(img_canvas, scene_data, t):
    zoom = scene_data["zoom_start"] + (scene_data["zoom_end"] - scene_data["zoom_start"]) * t
    pan_x = scene_data["pan_x"] * t * 100
    pan_y = scene_data["pan_y"] * t * 100
    
    crop_w = int(WIDTH / zoom)
    crop_h = int(HEIGHT / zoom)
    
    center_x = img_canvas.width // 2 + int(pan_x)
    center_y = img_canvas.height // 2 + int(pan_y)
    
    x0 = center_x - crop_w // 2
    y0 = center_y - crop_h // 2
    x1 = x0 + crop_w
    y1 = y0 + crop_h
    
    x0 = max(0, min(img_canvas.width - crop_w, x0))
    y0 = max(0, min(img_canvas.height - crop_h, y0))
    x1 = x0 + crop_w
    y1 = y0 + crop_h
    
    cropped = img_canvas.crop((x0, y0, x1, y1))
    resized = cropped.resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
    
    final_frame = render_overlay(resized, scene_data, t)
    return final_frame

def main():
    print("🎬 Starting Lumina Vertical Short 9:16 Generation...")
    print(f"Target Output: {OUTPUT_VIDEO}")
    
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using FFmpeg: {ffmpeg_exe}")
    
    canvases = []
    for idx, scene in enumerate(SCENES):
        print(f"Loading asset {idx+1}/{len(SCENES)}: {scene['image']}")
        canvases.append(load_and_prepare_image(scene["image"]))
        
    frames_per_scene = int(SCENE_DURATION_SEC * FPS)
    fade_frames = int(FADE_DURATION_SEC * FPS)
    step_frames = frames_per_scene - fade_frames
    
    total_frames = step_frames * (TOTAL_SCENES - 1) + frames_per_scene
    total_duration = total_frames / FPS
    print(f"Total Frames: {total_frames} ({total_duration:.2f}s at {FPS} fps)")
    
    # 1. Synthesize audio track
    generate_ambient_audio(total_duration, TEMP_AUDIO)
    
    # 2. Launch FFmpeg process with video pipe and audio input
    ffmpeg_cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", TEMP_AUDIO,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        OUTPUT_VIDEO
    ]
    
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    
    current_scene = 0
    local_frame = 0
    
    for f in range(total_frames):
        t = local_frame / frames_per_scene
        frame_img = get_scene_frame(canvases[current_scene], SCENES[current_scene], t)
        
        if local_frame >= step_frames and current_scene < TOTAL_SCENES - 1:
            fade_t = (local_frame - step_frames) / fade_frames
            next_t = fade_t * (fade_frames / frames_per_scene)
            next_img = get_scene_frame(canvases[current_scene + 1], SCENES[current_scene + 1], next_t)
            
            frame_arr = (np.array(frame_img).astype(np.float32) * (1.0 - fade_t) +
                         np.array(next_img).astype(np.float32) * fade_t).astype(np.uint8)
        else:
            frame_arr = np.array(frame_img)
            
        proc.stdin.write(frame_arr.tobytes())
        
        local_frame += 1
        if local_frame >= frames_per_scene and current_scene < TOTAL_SCENES - 1:
            current_scene += 1
            local_frame = fade_frames
            
        if (f + 1) % 60 == 0 or (f + 1) == total_frames:
            print(f"Rendered frame {f+1}/{total_frames} ({(f+1)/total_frames*100:.1f}%)")
            
    proc.stdin.close()
    stderr_out = proc.stderr.read()
    proc.wait()
    
    if os.path.exists(TEMP_AUDIO):
        try:
            os.remove(TEMP_AUDIO)
        except Exception:
            pass
            
    if proc.returncode != 0:
        print(f"FFmpeg error: {stderr_out.decode('utf-8', errors='ignore')}")
        sys.exit(proc.returncode)
        
    size_bytes = os.path.getsize(OUTPUT_VIDEO)
    size_mb = size_bytes / (1024 * 1024)
    print("✅ Vertical 9:16 Short/Reel created successfully!")
    print(f"File: {OUTPUT_VIDEO}")
    print(f"Size: {size_mb:.2f} MB (Limit: < 8 MB)")
    print(f"Resolution: {WIDTH}x{HEIGHT} (9:16)")
    print(f"Duration: {total_duration:.2f} seconds")

if __name__ == "__main__":
    main()
