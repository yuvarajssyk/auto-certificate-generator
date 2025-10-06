document.getElementById("certForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const name = document.getElementById("name").value;
  const course = document.getElementById("course").value;
  const start = document.getElementById("start_date").value;
  const end = document.getElementById("end_date").value;

  // Default values
  const place = "Pondy";
  const regNo = "12345";
  const certNo = "98745621";
  const grade = "A";
  const regDate = new Date().toLocaleDateString();

  // Duration Calculation
  const startDate = new Date(start);
  const endDate = new Date(end);
  const diffDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
  const months = Math.floor(diffDays / 30);
  const duration = months > 0 ? `${months} Month(s)` : `${diffDays} Day(s)`;

  // Canvas setup
  const canvas = document.getElementById("certificateCanvas");
  const ctx = canvas.getContext("2d");

  const bg = new Image();
  bg.src = "images/cretificate_template.png";
  const sign1 = new Image();
  sign1.src = "images/sign_1.png";
  const sign2 = new Image();
  sign2.src = "images/sign_2.png";

  // Wait for images to load
  await Promise.all([
    new Promise((res) => (bg.onload = res)),
    new Promise((res) => (sign1.onload = res)),
    new Promise((res) => (sign2.onload = res)),
  ]);

  // Draw template background
  ctx.drawImage(bg, 0, 0, canvas.width, canvas.height);

  // Helper: convert fraction positions to pixels
  const toPixel = (frac, total) => Math.round(frac * total);

  // Font and color setup
  ctx.fillStyle = "black";
  ctx.textBaseline = "middle";

  // ---- TEXT POSITIONS (scaled to 1920x1080) ----
  const textPositions = {
    certi_no: [0.17, 0.08],
    reg_no: [0.87, 0.09],
    name: [0.43, 0.42],
    course: [0.43, 0.57],
    duration: [0.36, 0.66],
    start_date: [0.57, 0.66],
    end_date: [0.75, 0.66],
    grade: [0.20, 0.75],
    reg_date: [0.19, 0.80],
    place: [0.20, 0.84],
  };

  const fontSizes = {
    certi_no: 25,
    reg_no: 25,
    name: 50,
    course: 45,
    duration: 30,
    start_date: 30,
    end_date: 30,
    grade: 30,
    reg_date: 28,
    place: 28,
  };

  const data = {
    certi_no: certNo,
    reg_no: regNo,
    name,
    course,
    duration,
    start_date: start,
    end_date: end,
    grade,
    reg_date: regDate,
    place,
  };

  // Draw all text fields
  for (const [key, [xFrac, yFrac]] of Object.entries(textPositions)) {
    ctx.font = `bold ${fontSizes[key]}px Arial`;
    const x = toPixel(xFrac, canvas.width);
    const y = toPixel(yFrac, canvas.height);

    if (["name", "course"].includes(key)) {
      ctx.textAlign = "center";
    } else {
      ctx.textAlign = "left";
    }

    ctx.fillText(data[key], x, y);
  }

  // ---- SIGNATURE POSITIONS ----
  const signWidthFrac = 0.04; // same as Python
  const sign1Pos = [0.77, 0.73];
  const sign2Pos = [0.77, 0.83];
  const signWidth = canvas.width * signWidthFrac;

  // Draw signatures
  const drawSignature = (img, pos) => {
    const [xFrac, yFrac] = pos;
    const newW = signWidth;
    const newH = (newW / img.width) * img.height;
    const x = toPixel(xFrac, canvas.width) - newW / 2;
    const y = toPixel(yFrac, canvas.height) - newH / 2;
    ctx.drawImage(img, x, y, newW, newH);
  };

  drawSignature(sign1, sign1Pos);
  drawSignature(sign2, sign2Pos);

  // Display canvas + download button
  canvas.style.display = "block";
  document.getElementById("downloadBtn").style.display = "inline-block";
});

// --- Download Certificate ---
document.getElementById("downloadBtn").addEventListener("click", function () {
  const canvas = document.getElementById("certificateCanvas");
  const link = document.createElement("a");
  link.download = "certificate.png";
  link.href = canvas.toDataURL("image/png");
  link.click();
});
