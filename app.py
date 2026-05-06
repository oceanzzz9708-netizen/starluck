"""
星座运势查询 - Flask后端
"""
from flask import Flask, render_template, request, jsonify
import requests
import json
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL,
    CURRENT_PROVIDER
)

app = Flask(__name__)

# 十二星座列表
ZODIAC_SIGNS = [
    "白羊座", "金牛座", "双子座", "巨蟹座", "狮子座", "处女座",
    "天秤座", "天蝎座", "射手座", "摩羯座", "水瓶座", "双鱼座"
]

# 感情线场景
LOVE_SITUATIONS = ["暗恋", "暧昧", "恋爱中", "分手"]

# 事业线场景
WORK_SCENES = ["汇报", "合作", "冲突", "日常沟通"]


def call_llm(prompt):
    """调用LLM API生成运势内容"""
    if CURRENT_PROVIDER == "deepseek":
        api_key = DEEPSEEK_API_KEY
        api_url = DEEPSEEK_API_URL
        model = DEEPSEEK_MODEL
    else:
        api_key = DOUBAO_API_KEY
        api_url = DOUBAO_API_URL
        model = DOUBAO_MODEL

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"抱歉，发生了错误: {str(e)}"


def generate_love_fortune(my_sign, crush_sign, situation):
    """生成感情运势"""
    prompt = f"""你是一个专业的星座运势分析师。请根据以下信息，生成本周感情运势分析：

我的星座：{my_sign}
对方星座：{crush_sign}
当前阶段：{situation}

请生成一段简洁但有洞察力的运势分析，包含以下部分：
1. 本周信号（1-2句分析对方心理状态）
2. 本周建议（3条具体可执行的建议）
3. 本周避雷（1件不要做的事）
4. 本周时机（最佳互动时间建议）
5. 一句提醒（暖心的话）

要求：
- 语言温暖但有洞察力
- 建议要具体可执行
- 总字数控制在300字以内
- 不要使用emoji或特殊符号
- 直接输出分析内容，不需要标题

"""
    return call_llm(prompt)


def generate_career_fortune(my_sign, target_sign, scene):
    """生成事业运势"""
    prompt = f"""你是一个专业的星座职场分析师。请根据以下信息，生成本周事业运势分析：

我的星座：{my_sign}
对方星座：{target_sign}
当前场景：{scene}

请生成一段简洁但有洞察力的运势分析，包含以下部分：
1. 本周讯号（1-2句分析对方当前状态）
2. 本周建议（3条具体可执行的建议）
3. 本周话术（1-2句今天适合说的话）
4. 本周避坑（1件不要做的事）
5. 本周时机（最佳沟通时间建议）
6. 一句策略（犀利的职场提醒）

要求：
- 语言犀利但有帮助
- 建议要具体可执行
- 话术要自然不刻意
- 总字数控制在350字以内
- 不要使用emoji或特殊符号
- 直接输出分析内容，不需要标题

"""
    return call_llm(prompt)


@app.route('/')
def index():
    """返回首页"""
    return render_template('index.html')

@app.route('/test')
def test():
    return "Hello! The server is working. 🎉"


@app.route('/api/fortune', methods=['POST'])
def get_fortune():
    """获取运势分析"""
    data = request.get_json()

    fortune_type = data.get('type')  # 'love' 或 'career'

    if fortune_type == 'love':
        my_sign = data.get('my_sign')
        crush_sign = data.get('crush_sign')
        situation = data.get('situation')

        # 验证参数
        if not all([my_sign, crush_sign, situation]):
            return jsonify({'error': '请填写所有必填字段'}), 400
        if my_sign not in ZODIAC_SIGNS or crush_sign not in ZODIAC_SIGNS:
            return jsonify({'error': '请选择有效的星座'}), 400
        if situation not in LOVE_SITUATIONS:
            return jsonify({'error': '请选择有效的阶段'}), 400

        result = generate_love_fortune(my_sign, crush_sign, situation)

    elif fortune_type == 'career':
        my_sign = data.get('my_sign')
        target_sign = data.get('target_sign')
        scene = data.get('scene')

        # 验证参数
        if not all([my_sign, target_sign, scene]):
            return jsonify({'error': '请填写所有必填字段'}), 400
        if my_sign not in ZODIAC_SIGNS or target_sign not in ZODIAC_SIGNS:
            return jsonify({'error': '请选择有效的星座'}), 400
        if scene not in WORK_SCENES:
            return jsonify({'error': '请选择有效的场景'}), 400

        result = generate_career_fortune(my_sign, target_sign, scene)

    else:
        return jsonify({'error': '无效的运势类型'}), 400

    return jsonify({
        'success': True,
        'result': result
    })


# ... 你原来的代码保持不变 ...

if __name__ == '__main__':
    import os
    # Railway 常用 8080，如果 PORT 没有就默认 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
