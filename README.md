# PvZ2 植物双语学习图鉴

一个面向儿童与英语学习者的《Plants vs. Zombies 2》植物双语图鉴。项目将植物名称、属性、说明和重点词汇组织成可浏览、筛选、打印及导出 PDF 的学习卡。

> 非官方粉丝项目，与 Electronic Arts、PopCap Games 或《Plants vs. Zombies》品牌权利人不存在隶属、授权或认可关系。

## 功能

- 收录 213 种植物的中英文名称、世界、家族、阳光消耗、冷却、生命、伤害、索敌范围、说明与叶绿素效果等资料。
- 按游戏世界、薄荷家族和关键词筛选；植物卡可展开查看完整属性。
- 用彩色重点词与中文提示组成学习卡，适合看图记词、朗读和裁剪复习。
- 提供浏览器打印版：每页四张卡片、A4 竖版，可选择页码范围并导出 PDF。
- 提供独立的 A4 属性图鉴页，可按范围导出 PDF。
- 主要页面在本地优先加载图片；个别缺失素材会尝试使用数据中记录的远程备用地址。

## 快速开始

先准备 Node.js 18 或更高版本，然后在仓库根目录执行：

```bash
npm ci
npm run dev
```

终端会显示本地访问地址（通常是 `http://localhost:5173`）。打开后可使用：

- `/`：交互式植物学习图鉴；
- `/PvZ2_Plants_Ancient_Egypt_A4_Print.html`：四卡一页的 A4 打印版；
- `/PvZ2_Plants_Ancient_Egypt_Attributes.html`：A4 属性图鉴版。

生产构建：

```bash
npm run build
npm run preview
```

构建结果会写入 `dist/`，该目录已被 Git 忽略。

## 打印与导出

在两个 A4 页面顶部设置起止页码，点击 **Export PDF / 导出 PDF** 即可下载指定范围。也可以使用浏览器的打印功能；为获得正确比例，请选择 A4、关闭浏览器页眉页脚，并启用背景图形打印。

导出在浏览器中通过 `html2canvas` 与 `jsPDF` 完成。页数较多或设备性能较低时需要等待图片全部加载和逐页渲染。

## 项目结构

```text
.
├── plants_egypt.json                         # 植物数据的唯一事实来源
├── src/main.jsx                              # 交互式图鉴页面
├── src/print-book.js                         # A4 学习卡页面
├── src/attributes-book.js                    # A4 属性图鉴页面
├── src/export-a4-pdf.js                      # 浏览器端 PDF 导出逻辑
├── src/world-backgrounds.js                  # 世界背景映射
├── public/images/                            # 植物、家族图标和背景等第三方素材
├── scripts/sync_pvzg_data.py                 # 从本地 pvzg_site 副本同步数据/素材
├── scripts/fetch_pvz2_data.py                # 从配置的公开来源补全图片的维护脚本
├── build_html.py / build_pdf.py               # 早期静态 HTML/PDF 演示构建器
├── PVZGE_ATTRIBUTION.md                      # pvzg_site 的来源与归属说明
└── NOTICE                                    # 本项目的素材与商标声明
```

## 数据与素材维护

`plants_egypt.json` 是页面的主数据源。新增或修订内容时，应优先编辑数据而不是在 React 组件中硬编码植物信息。每条记录通常包含：

- 基础字段：`en`、`zh`、`sun`、`recharge`、`toughness`、`damage`、`range`；
- 学习字段：`sentence`、`sentence_zh`、`words`；
- 图鉴字段：`description`、`plant_food`、`family`、`world`、`elements`、`special`、`properties`；
- 图片字段：`pvzg_file`、`file` 和可选的 `img` 远程备用地址。

本地图片应放在 `public/images/` 中。页面会依次尝试 `pvzg_file`、`file`、`img`；请保留原始来源信息，并确认自己拥有再分发所需权利。维护脚本可能联网、下载或覆盖数据/素材，执行前请先检查参数和变更范围。

旧版静态构建器仍可用于演示或回归检查：

```bash
python3 -m json.tool plants_egypt.json >/dev/null
python3 build_html.py
python3 build_pdf.py  # 需要已安装 reportlab 与相应字体
```

它们生成的 HTML/PDF 是输出文件，不是主站点的构建流程；日常开发请使用 Vite 命令。

## 开发检查

提交前建议至少执行：

```bash
python3 -m json.tool plants_egypt.json >/dev/null
npm run build
```

并在浏览器中检查有代表性的世界与植物：图片是否加载、中文字体是否正常、窄屏筛选是否可用，以及 A4 页面中的文字、卡片和页码有没有溢出或裁切。

## 贡献

欢迎提交数据纠错、翻译改进、无障碍优化和版式修复。请保持 UTF-8 编码与 JSON 格式，使用描述性的 `snake_case` 文件名；涉及新图片时务必附上可核验的来源和许可证/授权信息。请不要提交游戏安装包、解包资源、密钥或大体积临时导出文件。

## 许可证与第三方权利

本仓库中由本项目贡献者原创的程序代码和文档，采用 [MIT License](LICENSE) 发布。`NOTICE`、`PVZGE_ATTRIBUTION.md` 和随附的 Apache-2.0 文本保留了已知的第三方归属信息。

**重要：`public/images/`、`plants_egypt.json` 中的第三方图片 URL，以及 `Plants vs. Zombies`、`Plants vs. Zombies 2` 名称、角色、美术和商标，不因 MIT 许可证而获得授权，也不在本项目的授权范围内。** 其中部分素材来自 `Gzh0821/pvzg_site`，其上游项目声明为 Apache-2.0；这不等同于获得 EA/PopCap 的底层游戏美术、角色或商标授权。

因此，本仓库是“代码开源、第三方游戏素材权利保留”的混合仓库，而不是所有文件都可自由再分发的纯开源素材包。若要把项目作为可无条件 fork、打包或商业使用的开源发行版，请在公开前移除这些素材，改用原创或已取得兼容开源许可证的替代图，或取得权利人的书面授权。EA 当前的内容政策仅在其条件下允许粉丝个人/非商业项目使用游戏内容，且保留其知识产权；发布或商用前应自行取得专业法律意见与必要许可。[EA 内容政策](https://help.ea.com/en/articles/security-and-rules/ea-content-policy/) · [EA 用户协议](https://www.ea.com/legal/user-agreement)

## 致谢

- 游戏相关角色、美术和商标：其各自权利人，包含 Electronic Arts / PopCap Games。
- 部分植物与背景素材：[`Gzh0821/pvzg_site`](https://github.com/Gzh0821/pvzg_site)，详见 [PVZGE_ATTRIBUTION.md](PVZGE_ATTRIBUTION.md)。
- 本项目使用 React、Vite、html2canvas、jsPDF 等开源软件，具体许可证以各依赖的发行信息为准。
