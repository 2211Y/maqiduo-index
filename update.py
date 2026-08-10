# -*- coding: utf-8 -*-
"""玛奇朵指数 · 每日自动更新脚本（零依赖，仅用标准库）

做什么：
  1. 首次运行：从 seed.json（原 HTML 固化的回测真值）注入历史底；
  2. 每天运行：拉腾讯财经实时行情 → 用同套四维度算法算指数 → 追加/更新到 data.json；
  3. 回测区间（seed 最后一天之前）内的日期保持固化真值，不被盘中实时值污染。

部署：用 GitHub Actions / 轻量云 cron / Windows 任务计划，每个交易日收盘后跑一次即可。
"""
import urllib.request, json, datetime, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, 'data.json')
SEED_PATH = os.path.join(HERE, 'seed.json')

# ===== 与 HTML 完全一致的阈值 =====
TH = {
    'turnover': [[6000, 0], [10000, 15], [15000, 35], [20000, 55], [25000, 72], [30000, 88], [36000, 100]],
    'pct': [[-1.5, 0], [-0.75, 20], [0, 40], [0.75, 60], [1.5, 80], [2.5, 100]],
    'smallPrem': [[-1.5, 0], [-0.75, 20], [0, 40], [0.75, 60], [1.5, 80], [2.5, 100]],
}
IDX = ['sh000001', 'sz399001', 'sh000300', 'sz399006', 'sh000852']


def piecewise(table, x):
    if x <= table[0][0]:
        return table[0][1]
    n = len(table)
    if x >= table[n - 1][0]:
        return table[n - 1][1]
    for i in range(n - 1):
        x0, y0 = table[i]
        x1, y1 = table[i + 1]
        if x0 <= x <= x1:
            t = (x1 - x0) and (x - x0) / (x1 - x0) or 0
            return y0 + (y1 - y0) * t
    return table[n - 1][1]


def fetch_quotes(codes):
    url = 'https://qt.gtimg.cn/q=' + ','.join(codes)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://finance.qq.com/',
    })
    raw = urllib.request.urlopen(req, timeout=15).read().decode('gbk', 'ignore')
    out = {}
    for line in raw.strip().split(';'):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'v_(\w+)="(.*)"', line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def parse(raw):
    f = raw.split('~')
    chg = float(f[32])
    amt = float(f[35].split('/')[2])
    return chg, amt


def compute():
    d = fetch_quotes(IDX)
    sh_c, sh_a = parse(d['sh000001'])
    sz_c, sz_a = parse(d['sz399001'])
    hs_c, _ = parse(d['sh000300'])
    cyb_c, _ = parse(d['sz399006'])
    zz_c, _ = parse(d['sh000852'])
    turnover = (sh_a + sz_a) / 1e8  # 亿元（两市之和）
    small_prem = zz_c - hs_c
    comps = {
        'turnover': round(piecewise(TH['turnover'], turnover)),
        'hs300': round(piecewise(TH['pct'], hs_c)),
        'cyb': round(piecewise(TH['pct'], cyb_c)),
        'smallPrem': round(piecewise(TH['smallPrem'], small_prem)),
    }
    index = round((comps['turnover'] + comps['hs300'] + comps['cyb'] + comps['smallPrem']) / 4)
    return {
        'date': datetime.date.today().strftime('%Y-%m-%d'),
        'value': index,
        'turnover': round(turnover),
        'hs300': round(hs_c, 2),
        'cyb': round(cyb_c, 2),
        'smallPrem': round(small_prem, 2),
        'comps': comps,
    }


def load_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, encoding='utf-8') as f:
            return json.load(f)
    return {'updated_at': '', 'index_history': [], 'amount_history': []}


def save_data(data):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    data = load_data()
    ih = data.setdefault('index_history', [])
    ah = data.setdefault('amount_history', [])

    # 首次注入回测底
    if not ih and os.path.exists(SEED_PATH):
        with open(SEED_PATH, encoding='utf-8') as f:
            seed = json.load(f)
        ih.extend(seed['index_history'])
        ah.extend(seed['amount_history'])
        print('已注入回测底：', len(ih), '个交易日')

    backtest_end = ih[-1]['date'] if ih else ''

    # 计算今天（若网络可用）
    try:
        rec = compute()
    except Exception as e:
        print('实时获取失败，仅保存历史底：', repr(e))
        data['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        save_data(data)
        return

    today = rec['date']
    ih_map = {r['date']: r for r in ih}
    ah_map = {r['date']: r for r in ah}

    if today in ih_map and today <= backtest_end:
        print('今天在回测区间内，保持固化真值，不覆盖')
    else:
        if today in ih_map:
            ih_map[today].update(rec)
        else:
            ih.append(rec)
        ah_rec = {'date': today, 'y': rec['turnover']}
        if today in ah_map:
            ah_map[today].update(ah_rec)
        else:
            ah.append(ah_rec)

    ih.sort(key=lambda r: r['date'])
    ah.sort(key=lambda r: r['date'])
    data['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_data(data)
    print('更新完成', today, '指数=', rec['value'], '成交额=', rec['turnover'], '亿')


if __name__ == '__main__':
    main()
