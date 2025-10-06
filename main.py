import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# ------------------- USER CONFIG -------------------
EXCEL_PATH    = r"data\datas.xlsx"       # Excel with student data
TEMPLATE_PATH = r"images/cretificate_template.png"           # New certificate template
SIGN1_PATH    = r"images/sign_1.png"     # Executive Director
SIGN2_PATH    = r"images/sign_2.png"     # BCT Director
OUTPUT_DIR    = "certificates"

# Font settings
FONT_PATH = "arial.ttf"
MIN_FONT_SIZE = 10
MAX_TEXT_WIDTH_FRAC = 0.80  # 80% of image width

FONT_SIZES = {
    "certi_no": 20,
    "reg_no": 20,
    "name": 30,
    "course": 30,
    "duration": 23,
    "reg_date": 23,
    "start_date": 23,
    "end_date": 23,
    "grade": 23,
    "place": 23,
}

# ---------------- TEXT POSITIONS -------------------
# (x_fraction, y_fraction) relative to template size
TEXT_POSITIONS = {
    "certi_no":   (0.17, 0.08),   # top-left "Certificate No:"
    "reg_no":     (0.87, 0.09),   # top-right "St. Reg. No"
    "name":       (0.43, 0.42),   # student name (center)
    "course":     (0.43, 0.57),   # course name (center)
    "duration":   (0.36, 0.66),   # "For the period of"
    "start_date": (0.57, 0.66),   # "From"
    "end_date":   (0.75, 0.66),   # "To"
    "grade":      (0.20, 0.75),   # "IN GRADE"
    "reg_date":   (0.19, 0.80),   # "ISSUED ON"
    "place":      (0.20, 0.84)    # "PLACE"
}
# Signature positions
SIGN1_POS = (0.77, 0.73)  # Executive Director
SIGN2_POS = (0.77, 0.83)  # BCT Director
SIGN_WIDTH_FRAC = 0.04
# ---------------------------------------------------

def to_pixel(value, total):
    v = float(value)
    return int(round(v * total)) if 0.0 < v <= 1.0 else int(round(v))

def fit_font_for_width(text, font_path, max_width_px, max_font_size, min_font_size=MIN_FONT_SIZE):
    """Find largest font size where text fits in max_width_px."""
    try:
        for size in range(max_font_size, min_font_size - 1, -1):
            f = ImageFont.truetype(font_path, size)
            tmp_img = Image.new("RGB", (10, 10))
            tmp_draw = ImageDraw.Draw(tmp_img)
            bbox = tmp_draw.textbbox((0, 0), text, font=f)
            if bbox[2] - bbox[0] <= max_width_px:
                return f
        return ImageFont.truetype(font_path, min_font_size)
    except Exception:
        return ImageFont.load_default()

def draw_text_at(draw, text, font, pos_frac, template_w, template_h, fill="black", align="center"):
    x = to_pixel(pos_frac[0], template_w)
    y = to_pixel(pos_frac[1], template_h)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    if align == "center":
        pos = (x - text_w // 2, y - text_h // 2)
    elif align == "left":
        pos = (x, y - text_h // 2)
    elif align == "right":
        pos = (x - text_w, y - text_h // 2)
    else:
        pos = (x, y)

    draw.text(pos, text, font=font, fill=fill)

def paste_signature(cert, sig_path, pos_frac, template_w, template_h):
    if not os.path.exists(sig_path):
        return
    sig = Image.open(sig_path).convert("RGBA")
    new_w = int(round(template_w * SIGN_WIDTH_FRAC))
    orig_w, orig_h = sig.size
    new_h = int(round((new_w / orig_w) * orig_h))
    sig = sig.resize((new_w, new_h), Image.LANCZOS)
    cx = to_pixel(pos_frac[0], template_w)
    cy = to_pixel(pos_frac[1], template_h)
    top_left = (int(cx - new_w / 2), int(cy - new_h / 2))
    cert.paste(sig, top_left, sig)

def make_certificates():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_excel(EXCEL_PATH)

    required_cols = ["CERTI NO","REG NO","NAME","COURSE","DURATION","REG DATE","START DATE","END DATE","GRADE","PLACE"]
    for c in required_cols:
        if c not in df.columns:
            raise ValueError(f"Missing required column: {c}")

    for idx, row in df.iterrows():
        cert = Image.open(TEMPLATE_PATH).convert("RGBA")
        w, h = cert.size
        draw = ImageDraw.Draw(cert)

        for field in TEXT_POSITIONS.keys():
            text_value = str(row[field.replace("_"," ").upper()]).strip()
            max_text_w = int(w * MAX_TEXT_WIDTH_FRAC)
            font = fit_font_for_width(text_value, FONT_PATH, max_text_w, FONT_SIZES[field])
            align = "center" if field in ["name","course"] else "left"
            draw_text_at(draw, text_value, font, TEXT_POSITIONS[field], w, h, align=align)

        paste_signature(cert, SIGN1_PATH, SIGN1_POS, w, h)
        paste_signature(cert, SIGN2_PATH, SIGN2_POS, w, h)

        safe_name = "".join(c for c in row["NAME"] if c.isalnum() or c in (" ", "_")).rstrip()
        out_path = os.path.join(OUTPUT_DIR, f"{safe_name}_certificate.png")
        cert.convert("RGB").save(out_path, quality=95)
        print(f"Certificate generated: {out_path}")

if __name__ == "__main__":
    make_certificates()

