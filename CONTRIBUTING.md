# 🤝 贡献指南

感谢您对 Sakura-Bot 项目的关注！我们欢迎任何形式的贡献。

---

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发流程](#开发流程)
- [提交规范](#提交规范)
- [代码规范](#代码规范)
- [测试指南](#测试指南)
- [问题报告](#问题报告)
- [功能请求](#功能请求)

---

## 🌟 行为准则

### 我们的承诺

为了营造开放和包容的环境，我们承诺让每个人都能参与到项目中来，无论其经验水平、性别、性别认同和表达、性取向、残疾、个人外貌、体型、种族、民族、年龄、宗教或国籍如何。

### 我们的标准

积极行为包括：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

不可接受的行为包括：

- 使用性化的语言或图像
- 恶意攻击或侮辱性评论
- 骚扰
- 未经许可发布他人的私人信息
- 其他不道德或不专业的行为

---

## 🚀 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请：

1. 检查 [现有的 issues](../../issues) 确保问题未被报告
2. 使用合适的 [Issue 模板](.github/ISSUE_TEMPLATE/) 创建新 issue
3. 提供尽可能详细的信息

### 提交代码

1. **Fork 项目**
   ```bash
   # 在 GitHub 上点击 Fork 按钮
   ```

2. **克隆到本地**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Sakura-Bot.git
   cd Sakura-Bot
   ```

3. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

4. **进行更改**
   - 遵循[代码规范](#代码规范)
   - 添加必要的测试
   - 更新相关文档

5. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

6. **推送到您的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 在 GitHub 上创建 PR
   - 使用 [PR 模板](.github/PULL_REQUEST_TEMPLATE.md)
   - 等待代码审查

---

## 🔄 开发流程

### 分支策略

- **main**: 主分支，稳定版本
- **dev**: 开发分支，最新功能
- **feature/***: 功能分支
- **fix/***: 修复分支
- **hotfix/***: 紧急修复分支

### 工作流程

1. 从 `dev` 分支创建功能分支
2. 在功能分支上开发
3. 提交到您的 Fork
4. 创建 PR 到 `dev` 分支
5. 通过代码审查后合并
6. 定期从 `dev` 合并到 `main`

---

## 📝 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- `feat`: 新功能
- `fix`: 问题修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具更新
- `build`: 构建系统
- `ci`: CI 配置
- `revert`: 回退提交

### 示例

```bash
# 新功能
git commit -m "feat(ai): 添加新的 AI 模型支持"

# 问题修复
git commit -m "fix(summary): 修复汇总消息格式错误"

# 文档更新
git commit -m "docs(readme): 更新安装说明"

# 代码重构
git commit -m "refactor(core): 优化错误处理逻辑"
```

### 详细的 Body

```bash
git commit -m "feat(qa): 添加问答历史记录功能

- 实现问答历史持久化存储
- 添加历史查询命令
- 支持历史记录导出

Closes #123"
```

---

## 🎨 代码规范

### Python 代码风格

我们遵循 [PEP 8](https://pep8.org/) 规范，使用以下工具：

#### Ruff (主要检查工具)

```bash
# 安装 ruff
pip install ruff

# 检查代码
ruff check .

# 自动修复
ruff check . --fix
```

#### isort (导入排序)

```bash
# 安装 isort
pip install isort

# 检查导入排序
isort --check-only .

# 自动修复
isort .
```

### 代码结构

```
Sakura-Bot/
├── core/              # 核心模块
├── tests/            # 测试文件
├── data/             # 数据文件
├── wiki/             # 文档
├── main.py           # 入口文件
├── qa_bot.py         # QA Bot 入口
└── requirements.txt  # 依赖列表
```

### 命名规范

- **模块/包**: `lowercase_with_underscores`
- **类**: `CapitalizedWords`
- **函数/方法**: `lowercase_with_underscores`
- **常量**: `UPPERCASE_WITH_UNDERSCORES`
- **私有方法**: `_leading_underscore`

### 文档字符串

使用 Google 风格的 docstrings：

```python
def summarize_channel(channel_id: str, messages: List[str]) -> str:
    """生成频道消息汇总
    
    Args:
        channel_id: 频道 ID
        messages: 消息列表
    
    Returns:
        汇总文本
    
    Raises:
        ValueError: 如果频道 ID 无效
    """
    pass
```

---

## 🧪 测试指南

### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-asyncio

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_module.py

# 生成覆盖率报告
pytest --cov=core --cov-report=html
```

### 编写测试

```python
# tests/test_example.py
import pytest

def test_example():
    """测试示例"""
    result = function_to_test()
    assert result == expected_value

@pytest.mark.asyncio
async def test_async_example():
    """异步测试示例"""
    result = await async_function()
    assert result is not None
```

---

## 🐛 问题报告

### 报告 Bug

请使用 [Bug Report 模板](.github/ISSUE_TEMPLATE/bug_report.md) 并提供：

1. 清晰的描述和复现步骤
2. 预期行为和实际行为
3. 环境信息（Python 版本、操作系统等）
4. 相关日志和错误信息
5. 截图（如果适用）

### 功能请求

请使用 [Feature Request 模板](.github/ISSUE_TEMPLATE/feature_request.md) 并说明：

1. 功能描述和使用场景
2. 详细的实现建议
3. 可能的替代方案
4. 优先级

---

## 📚 文档贡献

文档同样重要！您可以：

1. 修正错别字和错误
2. 改进现有文档的清晰度
3. 添加使用示例
4. 翻译文档

---

## 🎯 Pull Request 检查清单

提交 PR 前，请确认：

- [ ] 代码符合项目规范
- [ ] 包含必要的测试
- [ ] 所有测试通过
- [ ] 更新了相关文档
- [ ] 遵循提交信息规范
- [ ] PR 描述清晰完整
- [ ] 添加了适当的标签

---

## 💬 获取帮助

- 📖 查看 [Wiki](../wiki)
- 💬 参与 [Discussions](../../discussions)
- 🐛 查看 [Issues](../../issues)

---

## 📜 许可证

贡献的代码将采用项目的 [AGPL-3.0](LICENSE) 许可证。

---

## 🌈 致谢

感谢所有贡献者！您的贡献让 Sakura-Bot 变得更好。

[贡献者列表](../../graphs/contributors)