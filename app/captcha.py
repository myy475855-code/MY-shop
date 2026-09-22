"""
A real picture CAPTCHA: a short random code drawn onto a noisy, slightly
distorted PNG. The code is generated once per image request, stashed in the
user's session, and consumed (one-time use) when the form is submitted.

No external CAPTCHA service or API key needed — everything is rendered
locally with Pillow.
"""

import io
import random
import string

from flask import session
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SESSION_KEY = "captcha_code"

# Characters that are easy to mistype/misread are left out (0/O, 1/I/L).
_ALPHABET = "".join(ch for ch in (string.ascii_uppercase + string.digits) if ch not in "0O1IL")

_WIDTH = 180
_HEIGHT = 64
_CODE_LENGTH = 5


def _random_code(length=_CODE_LENGTH):
    return "".join(random.choices(_ALPHABET, k=length))


def _load_font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        # Older Pillow versions don't support a size argument on the default font.
        return ImageFont.load_default()


def generate_captcha_code():
    """Create a new code, store it in the session, and return it (rarely needed directly)."""
    code = _random_code()
    session[SESSION_KEY] = code
    return code


def verify_captcha(user_answer):
    """Check the submitted code against the session and consume it (one-time use)."""
    correct = session.pop(SESSION_KEY, None)
    if not correct or not user_answer:
        return False
    return user_answer.strip().upper() == correct


def render_captcha_png():
    """Generate a fresh code, store it in the session, and return PNG bytes for it."""
    code = generate_captcha_code()

    image = Image.new("RGB", (_WIDTH, _HEIGHT), color=(244, 245, 250))
    draw = ImageDraw.Draw(image)

    # Faint wavy background lines for noise.
    for _ in range(5):
        y_base = random.randint(6, _HEIGHT - 6)
        points = [(x, y_base + random.randint(-8, 8)) for x in range(0, _WIDTH + 10, 10)]
        draw.line(points, fill=tuple(random.randint(206, 226) for _ in range(3)), width=2)

    font = _load_font(34)

    # Draw each character on its own tile, rotate it a little, then paste.
    x_cursor = 10
    for ch in code:
        tile = Image.new("RGBA", (32, 48), (255, 255, 255, 0))
        tile_draw = ImageDraw.Draw(tile)
        color = (
            random.randint(30, 70),
            random.randint(35, 90),
            random.randint(120, 190),
        )
        tile_draw.text((3, 2), ch, font=font, fill=color)
        angle = random.randint(-24, 24)
        tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)

        y_cursor = random.randint(2, 14)
        image.paste(tile, (x_cursor, y_cursor), tile)
        x_cursor += random.randint(26, 32)

    # Speckle noise on top.
    for _ in range(90):
        px, py = random.randint(0, _WIDTH - 1), random.randint(0, _HEIGHT - 1)
        draw.point((px, py), fill=tuple(random.randint(160, 210) for _ in range(3)))

    image = image.filter(ImageFilter.SMOOTH)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf
