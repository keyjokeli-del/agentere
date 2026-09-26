"""
Automated Promo Reel Generator for Lumina Dental Studio
Generates a high-definition 1080x1080 promotional video reel (MP4)
from clinic assets with Ken Burns 3D camera pan/zoom, cross-dissolves,
clinical typography overlays, and a soothing ambient synthetic audio track (AAC).
Universal compatibility with Web, Instagram Reels, and YouTube Shorts (< 8 MB).
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
OUTPUT_VIDEO = os.path.join(ASSETS_DIR, "lumina-promo-reel.mp4")
TEMP_AUDIO = os.path.join(ASSETS_DIR, "temp_ambient.wav")

# Video Settings
WIDTH = 1080
HEIGHT = 1080
FPS = 30
SCENE_DURATION_SEC = 3.2
FADE_DURATION_SEC = 0.5
TOTAL_SCENES = 5

# Typography
FONT_BOLD_PATH = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REGULAR_PATH = "C:/Windows/Fonts/segoeui.ttf"

try:
    FONT_BADGE = ImageFont.truetype(FONT_BOLD_PATH, 24)
    FONT_TITLE = ImageFont.truetype(FONT_BOLD_PATH, 48)
    FONT_SUBTITLE = ImageFont.truetype(FONT_REGULAR_PATH, 26)
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
        "zoom_end": 1.12,
        "pan_x": 0.0,
        "pan_y": 0.0
    },
    {
        "image": "lumina-cover.png",
        "badge": "✦ CLÍNICA & TECNOLOGÍA DIGITAL",
        "title": "Diseño y Escaneo 3D",
        "subtitle": "Infraestructura de vanguardia y confort médico",
        "zoom_start": 1.08,
        "zoom_end": 1.18,
        "pan_x": -0.05,
        "pan_y": 0.02
    },
    {
        "image": "ig-post-blanqueamiento.png",
        "badge": "✦ ESTÉTICA CLÍNICA • $90 A $150 USD",
        "title": "Blanqueamiento Láser",
        "subtitle": "Sonrisa radiante y natural en una sola sesión",
        "zoom_start": 1.00,
        "zoom_end": 1.10,
        "pan_x": 0.02,
        "pan_y": -0.03
    },
    {
        "image": "ig-post-implantes.png",
        "badge": "✦ CIRUGÍA Y PRÓTESIS • $350 A $600 USD",
        "title": "Implantes Guiados 3D",
        "subtitle": "Fijación milimétrica en titanio y zafiro",
        "zoom_start": 1.02,
        "zoom_end": 1.14,
        "pan_x": -0.03,
        "pan_y": 0.02
    },
    {
        "image": "ig-post-urgencias.png",
        "badge": "✦ GUARDIA & TRIAGE 24/7 • INMEDIATO",
        "title": "Atención de Urgencias",
        "subtitle": "Chatea por WhatsApp • Agenda en Google Calendar",
        "zoom_start": 1.12,
        "zoom_end": 1.00,
        "pan_x": 0.0,
        "pan_y": 0.0
    }
]

def generate_ambient_audio(duration_sec, output_wav):
    """
    Generates a peaceful, soothing clinical ambient audio pad (A maj7 chord with soft shimmer envelope)
    """
    rate = 44100
    t = np.linspace(0, duration_sec, int(rate * duration_sec), False)
    
    # Peaceful harmonic frequencies: A (220Hz), C# (277.18Hz), E (329.63Hz), G# (415.3Hz), A (440Hz)
    chord = (
        0.35 * np.sin(2 * np.pi * 220.00 * t) +
        0.25 * np.sin(2 * np.pi * 277.18 * t) +
        0.25 * np.sin(2 * np.pi * 329.63 * t) +
        0.15 * np.sin(2 * np.pi * 415.30 * t) +
        0.10 * np.sin(2 * np.pi * 440.00 * t)
    )
    
    # Gentle breathing shimmer modulation (0.2 Hz)
    shimmer = 0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * t)
    audio = chord * shimmer * 0.15
    
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
        
    print(f"Generated synthetic ambient audio track: {output_wav}")

def load_and_prepare_image(filename):
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Asset not found: {path}")
    
    img = Image.open(path).convert("RGBA")
    
    canvas_w = int(WIDTH * 1.35)
    canvas_h = int(HEIGHT * 1.35)
    
    ratio = max(canvas_w / img.width, canvas_h / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - canvas_w) // 2
    top = (new_h - canvas_h) // 2
    img_cropped = img_resized.crop((left, top, left + canvas_w, top + canvas_h))
    
    return img_cropped

def render_overlay(frame_img, scene_data, t):
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    alpha_factor = min(1.0, t * 2.5)
    card_alpha = int(220 * alpha_factor)
    
    card_x0 = 60
    card_x1 = WIDTH - 60
    card_y0 = HEIGHT - 280
    card_y1 = HEIGHT - 70
    radius = 24
    
    draw.rounded_rectangle(
        [(card_x0, card_y0), (card_x1, card_y1)],
        radius=radius,
        fill=(COLOR_NAVY_BG[0], COLOR_NAVY_BG[1], COLOR_NAVY_BG[2], card_alpha),
        outline=(COLOR_CYAN_ACCENT[0], COLOR_CYAN_ACCENT[1], COLOR_CYAN_ACCENT[2], int(140 * alpha_factor)),
        width=2
    )
    
    badge_text = scene_data["badge"]
    badge_bg = (COLOR_CYAN_ACCENT[0], COLOR_CYAN_ACCENT[1], COLOR_CYAN_ACCENT[2], int(40 * alpha_factor))
    badge_border = (COLOR_CYAN_ACCENT[0], COLOR_CYAN_ACCENT[1], COLOR_CYAN_ACCENT[2], int(160 * alpha_factor))
    
    draw.rounded_rectangle(
        [(card_x0 + 30, card_y0 + 22), (card_x0 + 490, card_y0 + 58)],
        radius=10,
        fill=badge_bg,
        outline=badge_border,
        width=1
    )
    draw.text(
        (card_x0 + 45, card_y0 + 27),
        badge_text,
        font=FONT_BADGE,
        fill=(COLOR_CYAN_ACCENT[0], COLOR_CYAN_ACCENT[1], COLOR_CYAN_ACCENT[2], int(255 * alpha_factor))
    )
    
    draw.text(
        (card_x0 + 30, card_y0 + 72),
        scene_data["title"],
        font=FONT_TITLE,
        fill=(COLOR_WHITE[0], COLOR_WHITE[1], COLOR_WHITE[2], int(255 * alpha_factor))
    )
    
    draw.line(
        [(card_x0 + 30, card_y0 + 138), (card_x1 - 30, card_y0 + 138)],
        fill=(COLOR_CYAN_ACCENT[0], COLOR_CYAN_ACCENT[1], COLOR_CYAN_ACCENT[2], int(80 * alpha_factor)),
        width=1
    )
    
    draw.text(
        (card_x0 + 30, card_y0 + 152),
        scene_data["subtitle"],
        font=FONT_SUBTITLE,
        fill=(COLOR_SILVER[0], COLOR_SILVER[1], COLOR_SILVER[2], int(230 * alpha_factor))
    )
    
    return Image.alpha_composite(frame_img.convert("RGBA"), overlay).convert("RGB")

def get_scene_frame(img_canvas, scene_data, t):
    zoom = scene_data["zoom_start"] + (scene_data["zoom_end"] - scene_data["zoom_start"]) * t
    pan_x = scene_data["pan_x"] * t * 100
    pan_y = scene_data["pan_y"] * t * 100
    
    crop_w = int(WIDTH / zoom)
    crop_h = int(HEIGHT / zoom)
    
    cx = img_canvas.width / 2 + pan_x
    cy = img_canvas.height / 2 + pan_y
    
    x0 = int(cx - crop_w / 2)
    y0 = int(cy - crop_h / 2)
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
    print("Starting Lumina Promo Video Generation with Audio Track...")
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
    
    total_frames = frames_per_scene + (TOTAL_SCENES - 1) * step_frames
    total_duration = total_frames / FPS
    print(f"Total Frames: {total_frames} ({total_duration:.2f}s at {FPS} fps)")
    
    # 1. Generate ambient audio track
    generate_ambient_audio(total_duration, TEMP_AUDIO)
    
    # 2. Launch FFmpeg process with video pipe and audio file input
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
        "-crf", "21",
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
            frame_arr = np.array(frame_img, dtype=np.uint8)
            
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
    
    # Cleanup temp audio
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
    print("Video + Audio Reel created successfully!")
    print(f"File: {OUTPUT_VIDEO}")
    print(f"Size: {size_mb:.2f} MB (Limit: < 8 MB)")
    print(f"Duration: {total_duration:.2f} seconds")
    
if __name__ == "__main__":
    main()
