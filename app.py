from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import json
import random
from datetime import datetime
from gtts import gTTS

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
DATA_PATH = 'data.json'
AUDIO_DIR = 'static/audio'
os.makedirs(AUDIO_DIR, exist_ok=True)

# データ読み込み
def load_data():
    if os.path.exists(DATA_PATH) and os.path.getsize(DATA_PATH) > 0:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# データ保存
def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 音声生成
def generate_audio(text, id):
    tts = gTTS(text=text)
    audio_path = os.path.join(AUDIO_DIR, f"{id}.mp3")
    tts.save(audio_path)

@app.route('/')
def index():
    data = load_data()
    minimum_id = min(map(int, data.keys())) if data else None
    return render_template("index.html", minimum_id=minimum_id)

@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        data = load_data()
        # IDの自動決定（最大+1）
        if data:
            new_id = str(max(map(int, data.keys())) + 1)
        else:
            new_id = "1"

        text = request.form.get("text", "").strip()
        if not text:
            return "Text is required", 400

        # 語彙情報の構築
        vocabularies = []
        vocab_count = int(request.form.get("vocab_count", 0))
        for i in range(vocab_count):
            word = request.form.get(f"vocab_{i}_word", "").strip()
            pronunciation = request.form.get(f"vocab_{i}_pron", "").strip()
            meaning = request.form.get(f"vocab_{i}_meaning", "").strip()
            comment = request.form.get(f"vocab_{i}_comment", "").strip()
            if word:
                vocabularies.append({
                    "word": word,
                    "pronunciation": pronunciation,
                    "meaning": meaning,
                    "comment": comment
                })

        data[new_id] = {"text": text, "vocabularies": vocabularies, "created_at": datetime.today().strftime("%Y-%m-%d")}
        save_data(data)
        generate_audio(text, new_id)
        return redirect(url_for("index"))

    return render_template("add.html")

@app.route('/sentence_list')
def sentence_list():
    data = load_data()
    page = int(request.args.get("page", 1))
    per_page = 30

    sorted_items = sorted(data.items(), key=lambda x: int(x[0]))  # ID順に並べ替え
    total = len(sorted_items)
    total_pages = (total + per_page - 1) // per_page  # ceil割り

    start = (page - 1) * per_page
    end = start + per_page
    page_items = dict(sorted_items[start:end])

    return render_template(
        "sentence_list.html",
        page_sentences=page_items,
        total_pages=total_pages,
        current_page=page
    )

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    data = load_data()
    data_id = data.get(f"{id}")
    if not data_id:
        return "Sentence not found", 404

    text_before = data_id.get("text", "")
    time_before = data_id.get("created_at", "")

    if request.method == 'POST':
        new_text = request.form.get('text', '').strip()

        # 語彙の再構築（← POSTの中に移動）
        vocabularies = []
        vocab_count = int(request.form.get("vocab_count", 0))
        for i in range(vocab_count):
            word = request.form.get(f"vocab_{i}_word", "").strip()
            pronunciation = request.form.get(f"vocab_{i}_pron", "").strip()
            meaning = request.form.get(f"vocab_{i}_meaning", "").strip()
            comment = request.form.get(f"vocab_{i}_comment", "").strip()
            if word:
                vocabularies.append({
                    "word": word,
                    "pronunciation": pronunciation,
                    "meaning": meaning,
                    "comment": comment
                })

        # データ更新
        data[f"{id}"] = {
            "text": new_text,
            "vocabularies": vocabularies,
            "created_at": time_before
        }
        save_data(data)

        # 文が変更されたときは音声も更新
        if new_text != text_before:
            generate_audio(new_text, id)

        return redirect(url_for('sentence_list'))

    return render_template('edit.html', sentence=data_id)


@app.route('/dictation/<id>', methods=["GET", "POST"])
def dictation(id):
    data = load_data()
    ids = sorted(map(int, data.keys()))
    id_int = int(id)
    entry = data.get(str(id_int))
    if not entry:
        return "Invalid ID", 404

    if request.method == "POST":
        user_text = request.json.get("text", "").strip()
        is_correct = user_text.lower() == entry["text"].lower()
        return jsonify({
            "result": "Correct" if is_correct else "Incorrect",
            "correct": entry["text"],
            "vocabularies": entry.get("vocabularies", [])
        })

    # 前後のIDを探す
    idx = ids.index(id_int)
    prev_id = str(ids[idx - 1]) if idx > 0 else None
    next_id = str(ids[idx + 1]) if idx < len(ids) - 1 else None

    audio_file = url_for("static", filename=f"audio/{id}.mp3")
    return render_template("dictation.html", audio_file=audio_file, id=id, prev_id=prev_id, next_id=next_id)

@app.route('/dictation/shuffle/<int:index>', methods=["GET", "POST"])
def dictation_shuffle(index):
    data = load_data()
    ids = sorted(map(int, data.keys()))
    if not ids:
        return "No data available", 404
    
    if request.args.get("reset") == "1" or "shuffled_ids" not in session:
        session["shuffled_ids"] = random.sample(ids, len(ids))

    # セッションにシャッフル順がなければ新たに作成
    if "shuffled_ids" not in session:
        session["shuffled_ids"] = random.sample(ids, len(ids))

    shuffled_ids = session["shuffled_ids"]

    # 範囲外チェック
    if index < 0 or index >= len(shuffled_ids):
        return "Index out of range", 404

    current_id = str(shuffled_ids[index])
    entry = data.get(current_id)

    if not entry:
        return "Invalid ID", 404

    if request.method == "POST":
        user_text = request.json.get("text", "").strip()
        is_correct = user_text.lower() == entry["text"].lower()
        return jsonify({
            "result": "Correct" if is_correct else "Incorrect",
            "correct": entry["text"],
            "vocabularies": entry.get("vocabularies", [])
        })

    prev_index = index - 1 if index > 0 else None
    next_index = index + 1 if index < len(shuffled_ids) - 1 else None

    audio_file = url_for("static", filename=f"audio/{current_id}.mp3")
    return render_template("dictation.html",
                        audio_file=audio_file,
                        id=current_id,
                        prev_id=url_for("dictation_shuffle", index=prev_index) if prev_index is not None else None,
                        next_id=url_for("dictation_shuffle", index=next_index) if next_index is not None else None)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
