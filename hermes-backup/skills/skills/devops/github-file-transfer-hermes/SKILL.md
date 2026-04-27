---
name: github-file-transfer-hermes
description: 通过 GitHub HTTPS + PAT 让 Hermes Agent 与用户双向传输文件
---
# GitHub 文件传输通道配置

## 场景
让 Hermes Agent 通过 git push 将产出文件上传到用户的私有 GitHub 仓库，用户也能通过 git pull 或 GitHub 网页获取文件。

## 前置要求
- 用户有 GitHub 账号
- 用户在 GitHub 上创建了私有仓库（如 `HermesWork`）
- VPS 上已安装 git

## 操作步骤

### 1. 用户创建 GitHub PAT（需要正确 Scope）

**Token 创建路径**：GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

**必须勾选的 Scopes**：
- ✅ `repo` — 完整仓库读写权限
- ✅ `workflow` — 如果仓库有 `.github/workflows` 目录（否则 push 会报 `refusing to allow a Personal Access Token to create or update workflow` 错误）

**Token 格式**：`ghp_xxx`

### 2. VPS 配置 git 凭证

```bash
# 设置 git 用户信息
git config --global user.email "hermes@vps"
git config --global user.name "Hermes Backup"

# 存储凭证（永久有效）
git config --global credential.helper store
echo "https://github.com" > ~/.git-credentials
echo "https://用户名:TOKEN@github.com" >> ~/.git-credentials
```

### 3. 配置远程仓库

```bash
# 克隆用户仓库到本地（不要直接用 hermes-agent 主仓库的 remote）
cd /root/.hermes
git clone https://github.com/用户名/仓库名.git hermes-output
cd hermes-output
git remote -v  # 确认指向用户仓库
```

### 4. 验证双向通道

```bash
# Push 测试
echo "# Test" >> README.md
git add . && git commit -m "test" && git push

# Pull 测试
cd /tmp && git clone https://github.com/用户名/仓库名.git test-clone
```

## 常见错误

### `fatal: 'origin' does not appear to be a git repository`
原因：本地 git 没有正确设置 remote，或 remote URL 为空。
解决：`git remote add origin https://github.com/用户名/仓库名.git`

### `[remote rejected] HEAD -> main (refusing to allow a Personal Access Token to create or update workflow .github/workflows/xxx.yml without workflow scope)`
原因：PAT 缺少 `workflow` scope。
解决：删除旧 Token，重新生成并勾选 `workflow`。

### `Permission denied` / `Authentication failed`
原因：凭证未正确存储，或 Token 过期/无效。
解决：检查 `~/.git-credentials` 内容是否正确，重新配置凭证。

## 文件传输命令模板

```bash
cd /root/.hermes/hermes-output

# 上传文件
git add .
git commit -m "描述"
git push

# 更新本地（用户端有新文件时）
git pull origin main
```

## GitHub API 下载文件（无需 git clone）

```bash
curl -sL -H "Authorization: token TOKEN" \
  "https://api.github.com/repos/用户名/仓库名/contents/路径/文件名?ref=main" | \
  python3 -c "
import sys,json,base64
d=json.load(sys.stdin)
with open('/tmp/output.jpg','wb') as f:
    f.write(base64.b64decode(d['content']))
"
```

## 注意事项
- Token 要安全保管，不要在日志中明文输出
- 仓库必须是私有（private）防止信息泄露
- 如果不需要 git 历史，可以用 `git push --force` 覆盖
