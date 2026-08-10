# -*- coding: utf-8 -*-
"""一次性脚本：从原 HTML 提取固化回测真值，生成 seed.json（历史底）。
只用于初始化 data.json，平时不需要再跑。"""
import re, json, os

SRC = 'C:/Users/Yangning/Desktop/baoma-index.html'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seed.json')


def main():
    with open(SRC, encoding='utf-8') as f:
        html = f.read()
    # 提取 const BACKTESTS = { ... }; 中的对象字面量
    m = re.search(r'const BACKTESTS = (\{.*?\n\});', html, re.S)
    if not m:
        raise SystemExit('未找到 BACKTESTS')
    # JS 对象字面量（key/string 都用单引号）→ 换双引号即合法 JSON
    obj_text = m.group(1).replace("'", '"')
    # JS 对象内层 key（如 comps:{turnover:55}）无引号，补成 "turnover":55
    obj_text = re.sub(r'(\w+):', r'"\1":', obj_text)
    obj_text = re.sub(r',(\s*[}\]])', r'\1', obj_text)  # 去掉 JS 的尾随逗号
    data = json.loads(obj_text)

    index_history = []
    amount_history = []
    for mk, rows in data.items():
        for r in rows:
            index_history.append({
                'date': r['date'],
                'value': r['index'],
                'turnover': r['turnover'],
                'hs300': r['hs300'],
                'cyb': r['cyb'],
                'smallPrem': r['smallPrem'],
                'comps': r['comps'],
            })
            amount_history.append({'date': r['date'], 'y': r['turnover']})

    index_history.sort(key=lambda x: x['date'])
    amount_history.sort(key=lambda x: x['date'])
    seed = {'index_history': index_history, 'amount_history': amount_history}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(seed, f, ensure_ascii=False, indent=2)
    print('已生成 seed.json：共', len(index_history), '个交易日')


if __name__ == '__main__':
    main()
