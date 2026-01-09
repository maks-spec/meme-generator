import os
from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
import random
from datetime import datetime

app = Flask(__name__)

with open('templates/index.html', 'r', encoding='utf-8') as f:
    HTML_TEMPLATE = f.read()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TEMPLATES_FOLDER = os.path.join(BASE_DIR, 'static', 'templates')
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATES_FOLDER'] = TEMPLATES_FOLDER
app.config['STATIC_FOLDER'] = STATIC_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMPLATES_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

бегущая_строка = "Добро пожаловать на сайт meme generator! Сделайте свой мем прямо сейчас! Поддержи проект донатом!"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_font(size=40):
    possible_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()

def hex_to_rgb(value: str):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def generate_meme(image_path, text_top, text_bottom, text_top_x, text_top_y,
                  text_bottom_x, text_bottom_y, font_size, color, stroke_color):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = get_font(font_size)

    text_color = hex_to_rgb(color)
    stroke_color = hex_to_rgb(stroke_color)
    stroke_width = int(font_size * 0.08)

    if text_top:
        draw.text(
            (int(text_top_x), int(text_top_y)),
            text_top,
            font=font,
            fill=text_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color
        )

    if text_bottom:
        draw.text(
            (int(text_bottom_x), int(text_bottom_y)),
            text_bottom,
            font=font,
            fill=text_color,
            stroke_width=stroke_width,
            stroke_fill=stroke_color
        )

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], "meme.png")
    img.save(output_path)
    return output_path

def get_template_images():
    """Получает список изображений из папки templates"""
    templates = []
    if os.path.exists(TEMPLATES_FOLDER):
        for filename in os.listdir(TEMPLATES_FOLDER):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                templates.append({
                    'filename': filename,
                    'path': f'/static/templates/{filename}'
                })
    return templates

class SmartCaptionGenerator:
    def __init__(self):
        self.theme_keywords = {
            'животные': ['кот', 'собака', 'кошка', 'пёс', 'питомец', 'зверь', 'рыба', 'птица'],
            'еда': ['еда', 'бургер', 'пицца', 'суши', 'кофе', 'чай', 'десерт', 'мороженое'],
            'природа': ['природа', 'лес', 'гора', 'море', 'озеро', 'река', 'небо', 'солнце'],
            'люди': ['человек', 'люди', 'парень', 'девушка', 'ребенок', 'семья', 'друг'],
            'техника': ['телефон', 'компьютер', 'машина', 'ноутбук', 'гаджет', 'техника'],
            'мемы': ['мем', 'прикол', 'шутка', 'юмор', 'смех', 'ржач', 'рофл']
        }
        
        self.meme_templates = [
            # Шаблоны в стиле популярных мемов
            "Когда {} но {} 😂",
            "Этот момент, когда {} 💀",
            "{} быть как: {} 🎭",
            "Когда {} а {} 🔥",
            "{}: *{}* 👏",
            "Мой мозг: {} 🧠\nРеальность: {} 📌",
            "Ожидание: {} 🤔\nРеальность: {} 💥",
            "Когда {} и понимаешь, что {} 🚀",
            "{}: {} 🎯",
            "Понедельник: {} 😴\nПятница: {} 🎉",
            
            # Универсальные шаблоны
            "Идеальный {} не существует...\n{}: 🎨",
            "Когда {} на максимуме 🔥",
            "Этот {} изменит всё 💫",
            "{} уровня 'бог' 👑",
            "Когда {} и это нормально 👍",
            
            # Трендовые форматы
            "Шаблон: {} 📝\nИспользование: {} 🎪",
            "До: {} 😔\nПосле: {} 😎",
            "Я: {} 😐\n{}: {} 🤣",
            "Когда {} > {} 🏆",
            "{}: существует\n{}: 🚀"
        ]
        
        self.actions = {
            'животные': ['спит', 'ест', 'бегает', 'прыгает', 'смотрит', 'играет', 'прячется'],
            'еда': ['вкусно пахнет', 'манит', 'тает во рту', 'свежее', 'аппетитное'],
            'природа': ['прекрасно', 'завораживает', 'умиротворяет', 'вдохновляет'],
            'люди': ['улыбается', 'смеется', 'думает', 'работает', 'отдыхает'],
            'техника': ['работает', 'глючит', 'зависает', 'шумит', 'светится'],
            'мемы': ['виральный', 'смешной', 'залипательный', 'трендовый']
        }
        
        self.adjectives = [
            'идеальный', 'лучший', 'худший', 'невероятный', 'удивительный', 
            'странный', 'случайный', 'неожиданный', 'предсказуемый', 'легендарный',
            'эпичный', 'виральный', 'трендовый', 'случайный', 'абсурдный'
        ]
        
        self.emojis = ['😂', '🔥', '🎯', '💀', '👏', '🎨', '🚀', '💫', '🤯', '😍', '🤣', '👍']

    def analyze_filename(self, filename):
        """Анализ имени файла для определения темы"""
        if not filename:
            return ['мем', 'интернет']
            
        filename_lower = filename.lower()
        themes = []
        
        for theme, keywords in self.theme_keywords.items():
            if any(keyword in filename_lower for keyword in keywords):
                themes.append(theme)
        
        return themes if themes else ['мем', 'контент']

    def generate_captions(self, filename, file_size):
        """Генерация 5 уникальных подписей"""
        themes = self.analyze_filename(filename)
        primary_theme = themes[0] if themes else 'мем'
        
        captions = []
        attempts = 0
        max_attempts = 50
        
        while len(captions) < 5 and attempts < max_attempts:
            attempts += 1
            
            template = random.choice(self.meme_templates)
            adjective = random.choice(self.adjectives)
            action = random.choice(self.actions.get(primary_theme, ['происходит']))
            emoji = random.choice(self.emojis)
            
            # Создаем варианты заполнения шаблонов
            fill_options = [
                [adjective, primary_theme],
                [action, primary_theme],
                [f"{adjective} {primary_theme}", action],
                [primary_theme, adjective],
                [f"{action} {primary_theme}", adjective]
            ]
            
            for fills in fill_options:
                if len(fills) == template.count('{}'):
                    try:
                        caption = template.format(*fills)
                        # Добавляем эмодзи если его нет
                        if not any(e in caption for e in self.emojis):
                            caption += f" {emoji}"
                        
                        # Проверяем на уникальность и длину
                        if (caption not in captions and 
                            len(caption) <= 120 and 
                            len(caption) > 10):
                            captions.append(caption)
                            break
                    except:
                        continue
            
            if len(captions) >= 5:
                break
        
        # Если не получилось сгенерировать достаточно, добавляем запасные
        fallbacks = [
            f"Идеальный мем с {primary_theme}! {random.choice(self.emojis)}",
            f"Когда {primary_theme} на высоте! {random.choice(self.emojis)}",
            f"Этот {primary_theme} стоит запомнить! {random.choice(self.emojis)}",
            f"Виральный контент про {primary_theme}! {random.choice(self.emojis)}",
            f"Мем-шедевр с {primary_theme}! {random.choice(self.emojis)}"
        ]
        
        while len(captions) < 5:
            caption = random.choice(fallbacks)
            if caption not in captions:
                captions.append(caption)
        
        return captions[:5]

caption_generator = SmartCaptionGenerator()

def generate_ai_caption(image_filename=None, image_size=0):
    """Умная генерация подписей"""
    print(f"🎨 Генерируем подписи для: {image_filename}")
    
    try:
        captions = caption_generator.generate_captions(image_filename, image_size)
        print(f"✅ Сгенерировано: {len(captions)} подписей")
        for i, caption in enumerate(captions, 1):
            print(f"   {i}. {caption}")
        return captions
    except Exception as e:
        print(f"❌ Ошибка генерации: {e}")
        # Надежные запасные варианты
        return [
            "Креативная подпись для вашего мема! 🎨",
            "Идеально для вирального контента! 🚀",
            "Этот момент достоен мема! 📸",
            "Юморная подпись в процессе! 😄",
            "Мем-потенциал обнаружен! 🔥"
        ]

@app.route('/', methods=['GET', 'POST'])
def index():
    meme_url = None
    meme_filename = None

    if request.method == 'POST':
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            text_top = request.form.get('textTop', '')
            text_bottom = request.form.get('textBottom', '')
            text_top_x = request.form.get('textTop_x', 10)
            text_top_y = request.form.get('textTop_y', 10)
            text_bottom_x = request.form.get('textBottom_x', 10)
            text_bottom_y = request.form.get('textBottom_y', 400)
            font_size = int(request.form.get('font_size', 30))
            color = request.form.get('color', '#ffffff')
            stroke_color = request.form.get('stroke_color', '#000000')

            output_path = generate_meme(filepath, text_top, text_bottom,
                                        text_top_x, text_top_y,
                                        text_bottom_x, text_bottom_y,
                                        font_size, color, stroke_color)
            meme_filename = os.path.basename(output_path)
            meme_url = f"/uploads/{meme_filename}"

    template_images = get_template_images()
    
    return render_template('index.html',
                           бегущая_строка=бегущая_строка,
                           meme_url=meme_url,
                           meme_filename=meme_filename,
                           template_images=template_images)

@app.route('/get_templates')
def get_templates():
    """API endpoint для получения списка шаблонов"""
    templates = get_template_images()
    return jsonify(templates)

@app.route('/select_template', methods=['POST'])
def select_template():
    """Обработка выбора шаблона"""
    template_filename = request.json.get('template_filename')
    if template_filename:
        template_path = os.path.join(TEMPLATES_FOLDER, template_filename)
        if os.path.exists(template_path):
            import shutil
            meme_filename = f"selected_template_{template_filename}"
            output_path = os.path.join(UPLOAD_FOLDER, meme_filename)
            shutil.copy2(template_path, output_path)
            
            return jsonify({
                'success': True,
                'meme_url': f"/uploads/{meme_filename}",
                'filename': meme_filename
            })
    
    return jsonify({'success': False, 'error': 'Template not found'})

@app.route('/ai')
def ai_page():
    return render_template('ai.html', бегущая_строка=бегущая_строка)

@app.route('/ai/generate', methods=['POST'])
def ai_generate_caption():
    try:
        if 'image' not in request.files:
            return {'success': False, 'error': 'No image provided'}
        
        file = request.files['image']
        if file.filename == '':
            return {'success': False, 'error': 'No image selected'}
        
        print(f"📁 Обрабатываем файл: {file.filename}")
        
        file_size = len(file.read())
        file.seek(0)
        
        captions = generate_ai_caption(
            image_filename=file.filename,
            image_size=file_size
        )
        
        return {'success': True, 'captions': captions}
        
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        fallback = [
            "Креативная подпись для вашего мема! 🎨",
            "Идеально для вирального контента! 🚀",
            "Этот момент достоен мема! 📸",
            "Юморная подпись в процессе! 😄",
            "Мем-потенциал обнаружен! 🔥"
        ]
        return {'success': True, 'captions': fallback}

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/download/<filename>')
def download_meme(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename),
                     as_attachment=True)

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

@app.route('/donate')
def donate():
    return render_template('donate.html')

@app.route('/offline')
def offline():
    return render_template('offline.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)