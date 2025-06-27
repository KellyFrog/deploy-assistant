# 部署

**本项目仅适用于 Windows PowerShell.** 

- clone 本项目：

```
git clone ...
```

- 安装 requirements：

```
pip install -r requirements.txt
```

# 使用方法

请使用 python 3.12 运行。

- **运行**：打开项目文件夹，命令行输入命令

  `cd src`

  `python main.py`

  等待初始化完成后即可使用. 用户可以在不需要问询的情况下当成普通命令行使用.

  在不需要使用该命令行之时，输入命令

  `exit`

  即可.

  运行会默认在项目文件中开始运行，如果想在别的目录下运行，`cd 文件路径` 即可.

- **API Key 获取**：第一次运行的时候，会向用户查询硅基流动的 API Key. 正常输入后，API Key 将加密永久保存.

- **问询**：用户可以通过输入 `??` + 文字描述的命令问询在当前情境下应当做什么. 当对用户的需求有所疑问时，会向用户提出问题. 届时尽量清晰地回答问题即可. 否则，将提出若干个命令方案，用户需要输入一个范围内的阿拉伯数字表示所选择的方案，或者字符 Q 表示退出此次问询. 若选择了方案，则在经过安全性验证后，将自动执行该命令.

  示例情景：

  输入：

  ```
  ?? 让这个目录更加可爱
  ```

  输出：

  ```
  为了更好帮助您，可能需要您回答一下这个问题喵：请具体说明您想让目录如何显得更可爱？例如：添加装饰性文件/文件夹、修改图标、创建主题文档，还是其他形式？
  ```

  输入：

  ```
  添加一些装饰性的文件和文件夹
  ```

  输出：

  ```
  ================ 可用命令列表 ================
  【选项 0】
  ▶ 命令："    /\_/\n   ( o.o )n    > ^ <" | Out-File -FilePath .\cat_art.txt
  ✏️ 说明：生成猫咪ASCII艺术文本文件
  ❗️ 注意：需确保PowerShell版本支持n换行符转义
  ------------------------------
  【选项 1】
  ▶ 命令：New-Item -Path "小猫脚印" -ItemType Directory; New-Item -Path "小猫脚印\meow.txt" -Value "喵~ 这里超可爱！(=ↀωↀ=)"
  ✏️ 说明：创建小猫主题文件夹并添加喵叫文件
  ❗️ 注意：需要PowerShell环境，分号分隔多个命令
  ------------------------------
  
  请选择要执行的命令编号 (输入 Q 退出):
  ```
  
  输入 `0` 后自动检查安全性并执行命令 `"    /\_/\n   ( o.o )n    > ^ <" | Out-File -FilePath .\cat_art.txt`，后创建了 `cat_art` 文本文件.
  
- **部署帮助**：对于 github 仓库，用户可以通过输入 `deploy` + 仓库链接的命令问询用户该如何部署该 github 仓库. 由于下载方式的多样性，此处将不再直接给出可执行的命令，而是给出该如何操作的计划，用户可按照该计划手动执行.

  示例情景：

  输入：
  
  ```
  deploy https://github.com/AlwaySleepy/Garment-Pile
  ```
  
  输出：
  
  ```
  部署计划:
  1. 手动安装Isaac Sim 2023.1.1：下载后移动到~/.local/share/ov/pkg/并重命名为isaac-sim-2023.1.1，根据BUG_FIX.md修改meta-file
  2. 克隆仓库：git clone https://github.com/AlwaySleepy/Garment-Pile.git
  3. 手动下载Garment资产：从Google Drive链接下载并解压到Garment-Pile/Assets/目录
  4. 为Isaac Sim环境安装依赖：C:\Users\AD\.local\share\ov\pkg\isaac-sim-2023.1.1\python.sh -m pip install termcolor plyfile
  5. 创建conda环境：conda create -n garmentpile python=3.10
  6. 激活conda环境并安装PyTorch：conda activate garmentpile && pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118
  7. 安装项目依赖：cd Garment-Pile && pip install -r requirements.txt
  ```
  
  注释：若不理解，可将上述计划中的可以使用命令行完成的步骤喂给 `??`.

## 注意事项

- 由于存在记忆功能，在少数情况下输入命令后会有卡顿，属正常现象.
- 由于模拟终端本身限制，带有 emoji 等特殊字符的命令可能无法正常读取.
