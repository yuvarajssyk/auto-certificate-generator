from flask import Flask, render_template, request, send_from_directory, url_for
import os
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

from main import (
    TEMPLATE_PATH, SIGN1_PATH, SIGN2_PATH, FONT_PATH, FONT_SIZES,
    TEXT_POSITIONS, SIGN1_POS, SIGN2_POS, SIGN_WIDTH_FRAC,
    to_pixel, fit_font_for_width, draw_text_at, paste_signature
)

app = Flask(__name__)

EXCEL_PATH = "data/datas.xlsx"
OUTPUT_DIR = "certificates"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------- Helper Functions ----------------------
def get_next_numbers():
    """Auto-increment CERTI NO and REG NO"""
    if not os.path.exists(EXCEL_PATH):
        return "BCT-001", "ST-001"

    df = pd.read_excel(EXCEL_PATH)
    cert_numbers = df.get("CERTI NO", []).dropna().tolist() if "CERTI NO" in df.columns else []
    reg_numbers = df.get("REG NO", []).dropna().tolist() if "REG NO" in df.columns else []

    def next_code(code_list, prefix):
        if not code_list:
            return f"{prefix}-001"
        last_num = 0
        for c in code_list:
            try:
                last_num = max(last_num, int(str(c).split("-")[-1]))
            except:
                continue
        return f"{prefix}-{last_num + 1:03d}"

    return next_code(cert_numbers, "BCT"), next_code(reg_numbers, "ST")


def calculate_duration(start, end):
    """Calculate duration between start and end dates"""
    try:
        d1 = datetime.strptime(start, "%Y-%m-%d")
        d2 = datetime.strptime(end, "%Y-%m-%d")
        days = (d2 - d1).days
        months = days // 30
        if months > 0:
            return f"{months} Month(s)"
        else:
            return f"{days} Day(s)"
    except Exception:
        return "Duration"


def get_place_from_excel(name):
    """Fetch place from Excel"""
    if not os.path.exists(EXCEL_PATH):
        return "Chennai"

    df = pd.read_excel(EXCEL_PATH)
    if "NAME" not in df.columns or "PLACE" not in df.columns:
        return "Chennai"

    match = df[df["NAME"].str.lower() == name.lower()]
    if not match.empty:
        return match.iloc[0]["PLACE"]
    return "Pondy"


# ---------------------- Flask Routes ----------------------
@app.route("/", methods=["GET", "POST"])
def home():
    cert_url = None
    if request.method == "POST":
        name = request.form.get("name")
        course = request.form.get("course")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        certi_no, reg_no = get_next_numbers()
        duration = calculate_duration(start_date, end_date)
        place = get_place_from_excel(name)

        # Issue date = End date + 15 days
        issued_date = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=15)).strftime("%Y-%m-%d")

        data = {
            "CERTI NO": certi_no,
            "REG NO": reg_no,
            "NAME": name,
            "COURSE": course,
            "DURATION": duration,
            "REG DATE": datetime.today().strftime("%Y-%m-%d"),
            "START DATE": start_date,
            "END DATE": end_date,
            "ISSUED DATE": issued_date,
            "GRADE": "A",
            "PLACE": place
        }

        # Generate certificate image
        cert = Image.open(TEMPLATE_PATH).convert("RGBA")
        w, h = cert.size
        draw = ImageDraw.Draw(cert)

        for field in TEXT_POSITIONS.keys():
            val = str(data.get(field.replace("_", " ").upper(), ""))
            font = fit_font_for_width(val, FONT_PATH, int(w * 0.8), FONT_SIZES[field])
            align = "center" if field in ["name", "course"] else "left"
            draw_text_at(draw, val, font, TEXT_POSITIONS[field], w, h, align=align)

        paste_signature(cert, SIGN1_PATH, SIGN1_POS, w, h)
        paste_signature(cert, SIGN2_PATH, SIGN2_POS, w, h)

        safe_name = "".join(c for c in name if c.isalnum() or c in (" ", "_")).rstrip()
        output_path = os.path.join(OUTPUT_DIR, f"{safe_name}_certificate.png")
        cert.convert("RGB").save(output_path)

        cert_url = url_for('serve_certificate', filename=os.path.basename(output_path))

        # Optionally update Excel with this new record
        if os.path.exists(EXCEL_PATH):
            df = pd.read_excel(EXCEL_PATH)
        else:
            df = pd.DataFrame(columns=data.keys())
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_excel(EXCEL_PATH, index=False)

    return render_template("index.html", cert_url=cert_url)


@app.route("/certificates/<path:filename>")
def serve_certificate(filename):
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)
