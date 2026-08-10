# 玛奇朵指数

我自己搭的一个「散户情绪温度计」。分数 0 到 100，越高代表市场越亢奋、散户越上头，反过来提醒自己别跟着冲。

计算用的是几个公开的市场信号：成交额、沪深300、创业板、小盘股的相对强弱。每天收盘后自动算好，攒成一条历史曲线。

数据来自腾讯财经的公开行情接口，更新和托管都跑在 GitHub 上，所以任何能联网的手机或电脑都能打开看，不用我自己守着电脑。

## 里面有什么

- `index.html` —— 看板页面，直接打开就能看
- `update.py` —— 更新脚本，拉行情、算指数、写进 data.json，不依赖任何第三方库
- `data.json` —— 历史数据，前面是回测的 144 个交易日，之后每天自动往后加
- `seed.json` —— 回测用的底稿，第一次自动灌进 data.json，平时不用管
- `extract_seed.py` —— 一次性工具，把原始 HTML 里的回测数据抽出来生成 seed.json，跑过一次就不用了
- `.github/workflows/daily.yml` —— 自动跑更新的工作流

## 本地先看看

进到这个文件夹，执行：

```
python -m http.server 8000
```

然后浏览器打开 http://localhost:8000/ 。
注意别直接双击 html 用 file:// 打开，浏览器会拦掉数据请求，必须走本地服务器。

## 放到公网上（GitHub Pages）

想让别人也能看、并且每天自动更新，就走 GitHub Pages：

1. 在 GitHub 新建一个公开仓库，把整个文件夹传上去（index.html、update.py、data.json、seed.json、.github/ 这些都带上）。
2. 进仓库 Settings → Pages → Source，选 Deploy from a branch，分支选 main，目录选 /(root)，保存。
3. 等几分钟，访问 https://你的用户名.github.io/仓库名/ 就能看到。
4. 自动更新已经配好了：每个交易日北京时间 15:50，daily.yml 会跑一遍 update.py，把新的 data.json 提交回仓库，Pages 跟着重新发布。

一点说明：GitHub 的服务器在境外，能不能稳定拉到腾讯的行情接口，得实测。如果 Actions 里 update.py 拉取超时，页面本身还是能正常看（data.json 里已经有历史了），只是不再自动追加新数据。真遇到这种情况，就把仓库克隆到一台国内机器，用系统定时任务每天 15:50 跑 update.py 再 push 回去：

```
python update.py
git add data.json && git commit -m auto && git push
```

（git push 要提前配好凭据或 PAT。）

## 关于合规

这就是个数据展示，不是投资建议。
