# option-pricing-lab

`option-pricing-lab` 是一个基于 `numpy` 的迷你期权定价项目，对应 FITE7405 Assignment 3。

当前已实现：

- 欧式期权 Black-Scholes 定价
- 隐含波动率求解
- 几何平均亚式期权闭式解
- 算术平均亚式期权蒙特卡洛与控制变量
- 几何平均篮子期权闭式解
- 算术平均篮子期权蒙特卡洛与控制变量
- 美式期权二叉树定价
- KIKO put 拟蒙特卡洛定价与 Delta
- 可供后续 GUI 复用的服务层接口

## 项目结构

```text
src/option_pricing_lab/
  domain/
    contracts.py     # 领域输入规格与输出结果对象
  pricing/
    core.py          # 数值基础函数
    european.py      # 欧式期权与隐含波动率
    asian.py         # 亚式期权
    basket.py        # 篮子期权
    american.py      # 美式期权二叉树
    kiko.py          # KIKO 拟蒙特卡洛
  application/
    service.py       # 供 CLI / API / GUI 复用的应用服务
  api/
    app.py           # FastAPI app factory
    schemas.py       # API 请求响应模型
    routers/         # HTTP 路由
    errors.py        # HTTP 错误处理
  app.py             # 服务启动入口
tests/
```

## 使用

安装依赖：

```bash
uv sync
```

运行测试：

```bash
uv run pytest
```

运行入口：

```bash
uv run option-pricing-lab
```
