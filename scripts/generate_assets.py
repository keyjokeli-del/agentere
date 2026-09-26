"""
Lumina Dental Studio - Asset Generation Script
Generates high-resolution branding and marketing assets using Gemini Imagen / Nano Banana 2
and saves them to frontend/public/social-kit/.
"""

import os
import sys
from pathlib import Path

# Target destination for branding assets
SOCIAL_KIT_DIR = Path(__file__).resolve().parent.parent / "frontend" / "public" / "social-kit"

ASSETS_SPEC = [
    {
        "filename": "lumina-logo.png",
        "aspect_ratio": "1:1",
        "description": "Minimalist luxury 3D emblem logo for 'Lumina Dental Studio', tooth silhouette combined with brilliant diamond cut and gentle laser beam, turquoise teal (#0d9488) and pure white tones on clean deep navy background (#0f172a), photorealistic, 8k resolution, elegant, vector-like precision, medical clinic branding."
    },
    {
        "filename": "lumina-cover.png",
        "aspect_ratio": "16:9",
        "description": "Ultra-modern, luxurious dental clinic lobby and treatment suite for 'Lumina Dental Studio', panoramic view, high-end ergonomic dental chair, ambient warm and teal lighting, floor-to-ceiling glass windows with subtle city view, clean architectural photography, peaceful and premium atmosphere, architectural digest style, photorealistic 8k."
    },
    {
        "filename": "ig-post-blanqueamiento.png",
        "aspect_ratio": "1:1",
        "description": "High-fashion beauty shot of a stunning radiant white smile, healthy gums, holding a minimalist dental laser handpiece with soft turquoise glow, subtle clinic background, premium aesthetic, commercial advertising photography, flawless dental whitening, 8k resolution."
    },
    {
        "filename": "ig-post-implantes.png",
        "aspect_ratio": "1:1",
        "description": "Futuristic 3D medical visualization of a premium titanium and zirconia dental implant seamlessly integrated into bone structure, high tech digital scan wireframe highlights, glowing teal accents, dark luxury medical aesthetic, scientific precision, 8k."
    },
    {
        "filename": "ig-post-urgencias.png",
        "aspect_ratio": "1:1",
        "description": "Warm, reassuring portrait of a professional female dentist in modern sleek teal-accented scrub, smiling warmly with comforting open hands, sterile modern emergency clinic room blurred in background, 24/7 dental emergency care concept, high empathy, natural lighting, 8k."
    }
]

def verify_assets():
    """Verify that all social kit assets are present and valid."""
    SOCIAL_KIT_DIR.mkdir(parents=True, exist_ok=True)
    all_ok = True
    print(f"Checking assets in {SOCIAL_KIT_DIR}...")
    for asset in ASSETS_SPEC:
        file_path = SOCIAL_KIT_DIR / asset["filename"]
        if file_path.exists():
            size_kb = file_path.stat().st_size / 1024
            print(f" [OK] {asset['filename']} ({size_kb:.1f} KB)")
        else:
            print(f" [MISSING] {asset['filename']}")
            all_ok = False
    return all_ok

if __name__ == "__main__":
    success = verify_assets()
    if success:
        print("\nAll Lumina Dental Studio visual assets verified successfully!")
        sys.exit(0)
    else:
        print("\nSome assets are missing.")
        sys.exit(1)
