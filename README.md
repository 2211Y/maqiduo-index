# 玛奇朵指数 · 自动更新看板

> 一个**逆向散户情绪指标**看板（0–100 分）：成交暴量 + 小票疯炒 + 创业板大涨 = 散户过热 = 越该警惕。
> 数据来自腾讯财经行情，服务端每日收盘后自动计算并累积，**任何设备打开都看得到连续、完整的历史**，不再依赖人肉打开浏览器。

## 文件结构
- `index.html` —— 看板页面（打开它就能看）
- `update.py` —— 自动更新脚本（拉行情、算指数、写 data.json，零第三方依赖）
- `data.json` —— 历史数据（144 个回测交易日 + 每日自动追加）
- `seed.json` —— 回测底（首次自动注入 data.json，平时不用动）
- `extract_seed.py` —— 一次性工具：从原 HTML 提取回测真值生成 seed.json（已跑过，不用再跑）
- `.github/workflows/daily.yml` —— GitHub 自动托管工作流

## 一、本地先看效果（10 秒）
在本文件夹下执行：
```bash
python -m http.server 8000
```
浏览器打开 http://localhost:8000/ 即可。
> 注意：不能直接双击 html 用 `file://` 打开，浏览器会拦截 fetch 数据，必须走本地服务器。

## 二、免费公网托管（GitHub Pages，全自动）
目标：别人也能打开，且每天自动更新。

1. 在 GitHub 新建一个**公开仓库**（名字随意，如 `maqiduo-index`）。
2. 把本文件夹的全部内容上传到仓库（`index.html` / `update.py` / `data.json` / `seed.json` / `.github/` 等）。
3. 仓库 → **Settings → Pages → Source** 选 `Deploy from a branch` → 选 **main** 分支、**/ (root)** → Save。
4. 稍等几分钟，访问 `https://你的用户名.github.io/仓库名/` 就能看到公开看板。
5. 自动更新：`.github/workflows/daily.yml` 已配置每个交易日 15:30（北京时间）自动跑 `update.py` 并把新 `data.json` 提交回仓库，Pages 会自动重新发布。

> ⚠️ 一个重要前提：GitHub 的服务器在**境外**，能否稳定拉到腾讯财经接口（`qt.gtimg.cn`）**需要实测**。
> 如果 Actions 日志里 `update.py` 拉取超时/失败，公开页面**仍能正常看**（因为 `data.json` 已有历史），只是新数据不再自动追加。
> 此时改用方案三，在**国内机器**定时跑即可。

## 三、境外拉不到时的兜底（国内定时任务）
把仓库克隆到一台**国内云服务器 / 你的电脑**，用系统定时任务每天 15:30 跑：
```bash
python update.py
git add data.json && git commit -m auto && git push
```
（git push 需要事先配好凭据 / PAT。）这样数据由国内网络更新，再同步到 GitHub Pages 发布。

## 四、合规与变现边界（务必看完）
- 本看板是**数据 / 指标展示**，不是投资建议。页面已带"不构成投资建议"声明，发布时务必保留。
- 想靠它赚钱，请走「卖工具 / 卖内容」路线（会员订阅、付费数据、教学、卖代码模板），**不要做"我带你买、给你具体买卖点"**——个人无牌照做证券投资咨询属违法。
- 付费墙后面也只给数据 / 图表，不给买卖指令。
