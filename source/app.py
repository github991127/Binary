"""Flask 应用与 REST API。

提供前端所需的全部接口：主题、牌库、三个概率问题的计算。
"""

import logging
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from Probability import (  # noqa: N812
    _pct,
    problem1_score_distribution,
    problem2_group_probabilities,
    problem3_probabilities,
)
from cards import DeckError, load_deck
from list_themes import extra, theme, theme_css_name
from utils import resource_path

# 配置日志：INFO 级别，包含时间、级别、消息
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def create_app():
    """创建并配置 Flask 应用。"""
    app = Flask(
        __name__,
        template_folder=resource_path('templates'),
        static_folder=resource_path('static'),
    )
    # 保证中文 JSON 正常显示，避免 unicode 转义
    app.json.ensure_ascii = False

    @app.route('/')
    def index():
        """渲染首页，注入当前主题与字体配置。"""
        return render_template(
            'index.html',
            theme_file=theme_css_name(),
            font_family=extra['font_family'],
            font_size=extra['font_size'],
        )

    @app.route('/api/themes', methods=['GET'])
    def get_themes():
        """返回可用主题列表及当前默认主题索引。"""
        try:
            return jsonify({
                'ok': True,
                'themes': theme,
                'current': theme.index(theme_css_name()),
            })
        except Exception:
            logger.exception('Failed to load themes')
            return jsonify({'ok': False, 'error': '加载主题失败'}), 500

    @app.route('/api/deck', methods=['GET'])
    def api_deck():
        """返回牌库整体信息、所有牌的明细以及 52 种花色点数分组。"""
        try:
            deck = load_deck()
            return jsonify({
                'ok': True,
                'total': deck.total,
                'key_count': deck.key_count,
                'key_rate': str(deck.key_rate()),
                'key_rate_pct': _pct(deck.key_rate()),
                'available_tags': deck.available_tags,
                'tag_display_names': deck.tag_display_names,
                'rows': deck.rows,
                'groups': [
                    {
                        'suit': g['suit'],
                        'rank': g['rank'],
                        'color': g['color'],
                        'size': g['size'],
                        'keys': g['keys'],
                    }
                    for g in deck.groups
                ],
            })
        except DeckError as e:
            logger.warning('Deck error: %s', e)
            return jsonify({'ok': False, 'error': str(e)}), 400
        except Exception:
            logger.exception('Failed to load deck')
            return jsonify({'ok': False, 'error': '加载牌库失败'}), 500

    @app.route('/api/problem1', methods=['POST'])
    def api_problem1():
        """问题 1：一次性抽 a 张牌，计算得分 0、至少 1、...、至少 b 的概率。"""
        try:
            deck = load_deck()
            data = request.get_json(silent=True) or {}
            tags = _validate_tags(data.get('tags'), deck)
            view = deck.with_tags(tags)
            a = _validate_draw(data.get('a'), view)
            b = _validate_b(data.get('b'), a)
            result = problem1_score_distribution(view['total'], view['key_count'], a, b)
            return jsonify({'ok': True, **result})
        except ValueError as e:
            return jsonify({'ok': False, 'error': str(e)}), 400
        except DeckError as e:
            return jsonify({'ok': False, 'error': str(e)}), 400
        except Exception:
            logger.exception('Problem1 calculation failed')
            return jsonify({'ok': False, 'error': '计算失败'}), 500

    @app.route('/api/problem2', methods=['POST'])
    def api_problem2():
        """问题 2：返回 52 种花色点数组合下抽到关键牌的概率。"""
        try:
            deck = load_deck()
            data = request.get_json(silent=True) or {}
            tags = _validate_tags(data.get('tags'), deck)
            view = deck.with_tags(tags)
            groups = problem2_group_probabilities(view['groups'])
            return jsonify({
                'ok': True,
                'N': view['total'],
                'K': view['key_count'],
                'groups': groups,
            })
        except ValueError as e:
            return jsonify({'ok': False, 'error': str(e)}), 400
        except DeckError as e:
            return jsonify({'ok': False, 'error': str(e)}), 400
        except Exception:
            logger.exception('Problem2 calculation failed')
            return jsonify({'ok': False, 'error': '计算失败'}), 500

    @app.route('/api/problem3', methods=['POST'])
    def api_problem3():
        """问题 3：对比新手与高手策略的得分概率。"""
        try:
            deck = load_deck()
            data = request.get_json(silent=True) or {}
            tags = _validate_tags(data.get('tags'), deck)
            view = deck.with_tags(tags)
            a = _validate_draw(data.get('a'), view)
            result = problem3_probabilities(view['total'], view['key_count'], view['groups'], a)
            return jsonify({'ok': True, **result})
        except ValueError as e:
            return jsonify({'ok': False, 'error': str(e)}), 400
        except DeckError as e:
            return jsonify({'ok': False, 'error': str(e)}), 400
        except Exception:
            logger.exception('Problem3 calculation failed')
            return jsonify({'ok': False, 'error': '计算失败'}), 500

    return app


def _parse_int(value, label):
    """解析用户输入为整数。

    拒绝空值、浮点数（如 3.5）以及非数字字符串，返回中文错误信息。
    """
    if value is None or value == '':
        raise ValueError(f'请输入有效的{label}')
    try:
        n = int(value)
        # Python int(3.5) == 3 会静默截断，这里显式拒绝浮点数
        if isinstance(value, float):
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError(f'{label} 必须是整数')
    return n


def _validate_draw(a, view):
    """校验抽牌数 a：非负整数且不超过总牌数。"""
    a = _parse_int(a, '抽牌数 a')
    if a < 0:
        raise ValueError('抽牌数 a 必须为非负整数')
    if a > view['total']:
        raise ValueError(f'抽牌数 a 不能大于总牌数 {view["total"]}')
    return a


def _validate_b(b, a):
    """校验最大得分 b：非负整数且不超过抽牌数 a。"""
    b = _parse_int(b, '最大得分 b')
    if b < 0:
        raise ValueError('最大得分 b 必须为非负整数')
    if b > a:
        raise ValueError('最大得分 b 不能大于抽牌数 a')
    return b


def _validate_tags(tags, deck):
    """校验前端传回的 tag 列表：必须是 list/set，且每个 tag 必须存在。"""
    if tags is None:
        return []
    if not isinstance(tags, (list, tuple, set)):
        raise ValueError('tags 必须是列表')
    available = set(deck.available_tags)
    invalid = [t for t in tags if t not in available]
    if invalid:
        raise ValueError('未知的 tag：' + '、'.join(invalid))
    return list(tags)


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
