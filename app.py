from flask import Flask, jsonify, request, send_file
from google import genai

app = Flask(__name__)
client = genai.Client()  # reads GEMINI_API_KEY from your environment

PROMPT = """You write Facebook captions in natural, friendly Bangla
for small sellers in Bangladesh.

Write 3 different short captions for the product below.
Each caption should sound like a real person wrote it, not a translation.
Add 5 hashtags at the end of each caption.
If a business name is given, mention it naturally once in the caption text,
and also make exactly one of the 5 hashtags the business name itself
(write it as one hashtag with no spaces, and use it only once in the hashtags).
If a price is given, include it in each caption.
If the business name or price is empty, just leave it out.
Separate the 3 captions with a line that contains only ---
Write nothing else, no titles and no explanations.

Business name: {business}
Product: {product}
Price: {price}"""


@app.get("/")
def home():
    return send_file("index.html")


@app.post("/caption")
def caption():
    data = request.get_json(silent=True) or {}
    business = (data.get("business") or "").strip()[:80]
    product = (data.get("product") or "").strip()[:300]
    price = (data.get("price") or "").strip()[:40]

    if not product:
        return jsonify(error="empty product"), 400

    try:
        interaction = client.interactions.create(
            model="gemini-3.5-flash",
            input=PROMPT.format(business=business, product=product, price=price),
        )
    except Exception as e:
        print("AI error:", e)
        return jsonify(error="ai failed"), 502

    text = interaction.output_text
    if not text:
        return jsonify(error="no text from ai"), 502

    captions = [c.strip() for c in text.split("---") if c.strip()]
    return jsonify(captions=captions)


if __name__ == "__main__":
    app.run(debug=False)