import logging
from pathlib import Path

from flask import Flask, jsonify, render_template, request

import Binary
from list_themes import extra, theme, theme_css_name
from utils import resource_path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(
        __name__,
        template_folder=resource_path('templates'),
        static_folder=resource_path('static'),
    )
    # 保证中文 JSON 正常显示
    app.json.ensure_ascii = False

    @app.route('/')
    def index():
        return render_template(
            'index.html',
            theme_file=theme_css_name(),
            font_family=extra['font_family'],
            font_size=extra['font_size'],
        )

    @app.route('/api/themes', methods=['GET'])
    def get_themes():
        try:
            return jsonify({
                'themes': theme,
                'current': theme.index(theme_css_name()),
            })
        except Exception as e:
            logger.exception('Failed to load themes')
            return jsonify({'error': '加载主题失败'}), 500

    def _convert(value, converter, label):
        try:
            result = converter(value)
            return jsonify({'result': result})
        except ValueError as e:
            logger.warning('%s conversion error: %s (input=%r)', label, e, value)
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception('%s conversion failed', label)
            return jsonify({'error': f'转换失败：{e}'}), 500

    @app.route('/api/binary-to-decimal', methods=['POST'])
    def binary_to_decimal_route():
        data = request.get_json(silent=True) or {}
        value = data.get('value', '')
        return _convert(value, Binary.binary_to_decimal, 'binary-to-decimal')

    @app.route('/api/decimal-to-binary', methods=['POST'])
    def decimal_to_binary_route():
        data = request.get_json(silent=True) or {}
        value = data.get('value', '')
        return _convert(value, Binary.decimal_to_binary, 'decimal-to-binary')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
