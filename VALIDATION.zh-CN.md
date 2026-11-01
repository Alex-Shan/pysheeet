# 中文化验证记录（Chinese Localization Validation）

## 基线与内容（Baseline and Content）

- 英文基线：`99dfbfff7c4bde7e43c9b9b5244da078e13b9158`。
- 66 篇网站文档、844 个章节；根目录和子目录的 6 份 README。
- `legacy-anchors.json` 保留原 HTML 锚点及 Sphinx 引用标签，README 保留原章节目标。
- 原始示例字符串、输出、API、命令、docstring 和依赖声明保持原样；翻译说明性注释。
- 可编辑 SVG 图表已翻译说明标签；原始截图、动画和性能图保留数据，附中文图例。

## 构建与静态检查（Build and Static Checks）

- Python 3.12.14；独立依赖声明与带哈希的完整锁文件。
- 全新环境按锁文件安装后，严格 Sphinx 构建成功。
- 66 篇页面及 844 个章节的双语标题与目录一致。
- 原有正文 HTML 锚点、内部链接、目标片段与静态资源检查通过。
- 全部文档代码块的非注释内容与基线一致；源码 Python AST、tokens 及其他语言非注释内容检查通过。
- `git diff --check` 通过；`requirements.txt` 未修改。

## 运行与浏览器检查（Runtime and Browser Checks）

- 原有 Python 示例测试：536 项通过，6 项因平台或可选依赖条件跳过。
- 原有 Flask 测试：18 项通过。
- 浏览器宽度：1440、1024、390、320 像素。
- 已检查：长目录、固定侧栏、手机折叠目录、页首目录按钮、上下滚动高亮、目录条目自动可见、正文位置稳定、键盘可操作控件、旧锚点直达、浏览历史、搜索、复制、语法高亮、首页和 404 页面。
- 已目视核查桌面与手机截图，并检查手机标题不被目录遮挡。
- GPU、LLM 集群和本机未配置的完整 CMake 工程未运行；其示例非注释内容保持基线一致。原仓库 CI 继续负责原有构建测试。

## 外部来源与发布核对（External Sources and Deployment Verification）

- 外链检查与内部链接检查分开执行；已修复 Megatron Bridge、vLLM Router、SGLang benchmark 目录和 Python Mapping Types 章节等已确认迁移的来源链接。
- registry 中已不可访问的 raytop 包链接改为项目安装说明，保留原有安装命令。
- GitHub 的动态行号片段可能无法由 Sphinx 静态解析；保留指向指定提交的原始引用。
- Pages 工作流只发布 `lang/cn`，Pull Request 仅验证。
- 发布成功后以线上 `version.json`、Actions 部署记录及实际页面复核；线上验证使用同一浏览器检查脚本。
