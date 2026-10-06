# PECR 新版论文：Raw + Arithmetic44

从用户提供的 `main-2.tex` 改写，旧文件完整保存在 `source/main-2.original.tex`。新主张是三世界回答的算术证据对应与错误诊断，保留原稿摘要、引言中“自信一致仍可能错”的叙事主线。

## 直接使用

- **`main.pdf`**：可阅读的双栏全文预览，包含附录。三张图按用户要求暂不制作，用占位框保持位置。
- **`main_single_file.tex`**：包含全部表格、参考文献和 ACL fallback 的单文件版，可直接上传或粘贴到 LaTeX 编辑器；无需 BibTeX。
- **`main.tex` + `tables/`**：分文件版，适合持续改稿。已编译无未定义引用、无公式/表格溢出。
- `body.tex`：正文编辑入口；`python scripts/assemble.py` 重新生成上述两份 main。
- `REVISION_NOTES.md`：主线、旧表映射、claim-evidence 对应和五维自审。
- `tables/`：10 个自动生成表文件；另有正文中的特征定义和额外模型汇总表。
- `audit/`：来源哈希、额外统计来源、编译与内容检查、PDF 页面预览。

当前占位图版正文结束在第8页，Limitations 与 References 在其后，全文含附录14页。接入真实图片后页数可能改变；这不是已经完成图稿和匿名发布的最终投稿版。作者仍沿用旧稿的 Discussion draft。

## 本次补充实验

完整结果位于同级目录 `pecr_raw44_attribution_controls_v1_20261007/`。两条轨道固定90次HGB拟合，Raw、Curve、Raw+44的既有OOF均逐项精确复现。测试G96、G96+构造元数据、G96+Raw16、再加h,t；另报告历史Raw17的三项兼容诊断。没有新API请求，也未读取gold或holdout。

| AUROC | Qwen3.5-4B | DeepSeek V4.1 Flash |
|---|---:|---:|
| G96 | .7379 | .7260 |
| G96 + construction metadata | .7421 | .7386 |
| G96 + Raw16 | .8023 | .7819 |
| Raw：G96 + Raw16 + h,t | .8035 | .7818 |
| Raw + Arithmetic44 | .8294 | .8068 |

历史Raw17的第17列是来源未对齐的构造描述符，当前主结果已排除它。因此正文采用准确的Raw16命名，历史Raw17阶梯放附录；没有悄悄改动主方法的维数。

## 再生成与编译

在项目工作区中运行 `python scripts/generate_tables.py` 从同级发布包和补充实验生成表格，再运行 `python scripts/assemble.py`。数值来源文件的哈希记录在 `audit/TABLE_SOURCES.json`。表格生成依赖NumPy；不涉及训练或模型调用。

编译 `main.tex` 或 `main_single_file.tex` 即可；常规LaTeX环境使用pdfLaTeX，本文在本机通过Tectonic 0.17.0编译验证。若目录内有acl.sty，会使用其preprint模式；否则使用原稿保留的inline ACL fallback。投稿时应换成当轮正式模板与匿名配置。

本目录不含模型输出原文、财报全文、API key、checkpoint或新benchmark压缩包。旧稿、冻结数据、主OOF均未覆盖，也没有自动推送GitHub。
