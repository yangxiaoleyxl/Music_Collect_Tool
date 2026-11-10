<h1 align="center">MusicDownload</h1>

<p align="center">
  🇺🇸 <a href="./README_EN.md">English</a> | 🇨🇳 <a href="./README.md">简体中文</a>
</p>

<p align="center">
<a href="https://peps.python.org/pep-0719"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/musicdl">
</a>
 <a href="https://pypi.org/project/musicdl"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/musicdl">
</a>
 <a href="https://github.com/MrsEWE44/musicDownload/releases"><img alt="GitHub Release" src="https://img.shields.io/github/v/release/MrsEWE44/musicDownload"></a>
 <a><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/MrsEWE44/musicDownload?style=flat"></a>
 <a><img alt="GitHub forks" src="https://img.shields.io/github/forks/MrsEWE44/musicDownload?style=flat"></a>
 <a><img alt="GitHub Downloads (all assets, all releases)" src="https://img.shields.io/github/downloads/MrsEWE44/musicDownload/total"></a>
 <a><img alt="GitHub watchers" src="https://img.shields.io/github/watchers/MrsEWE44/musicDownload?style=flat"></a>
 
</p>

宇宙超级无敌音乐下载器，支持无损音乐文件下载、批量下载、一键下载，支持歌单下载。

支持酷狗、酷我、QQ音乐、网易云、咪咕等主流音乐平台音乐搜索、下载。支持无损音乐文件下载。


图形界面基于 [musicdl](https://github.com/CharlesPikachu/musicdl)，由 [musicdlgui.py](https://github.com/CharlesPikachu/musicdl/blob/master/examples/musicdlgui/musicdlgui.py) 修改而来，上游仓库是 [MrsEWE44/musicDownload](https://github.com/MrsEWE44/musicDownload)。

这个副本额外提供不依赖 PySide6 的命令行入口。命令行需要 Python 3.10 或更高版本。


### 软件截图:

<table align="center" border="0" cellpadding="10">

  <tr>
    <td align="center">
      <img src="images/1.png" width="350"><br>
      <b>图片1</b>
    </td>
    <td align="center">
      <img src="images/2.png" width="350"><br>
      <b>图片2</b>
    </td>
    <td align="center">
      <img src="images/3.png" width="350"><br>
      <b>图片3</b>
    </td>
  </tr>
</table>

### 命令行

```bash
git clone <你的仓库地址>
cd musicDownload
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-cli.txt

python musicdownload_cli.py search 周杰伦 --sources netease --limit 5
python musicdownload_cli.py download 周杰伦 --sources netease --limit 6 --all --versions 3 --format flac --out ./已下载音乐
```

`--versions 3` 表示同一个歌名最多保存 3 个版本。`--format` 可以是 `mp3`、`flac`、`wav`、`m4a` 或 `any`。分语种批量下载：

```bash
FORMAT=flac ./download_by_language.sh ./已下载音乐 234
```

第二个参数是每个语种的上限。`234` 乘以 7 个语种等于 1638 首。音频会写到 `./已下载音乐/<语种>`。

### 图形界面

图形界面需要另外安装 PySide6，见 `requirements.txt`。

### 使用教程：

```bash
# 需要用Python3.13
git clone https://github.com/MrsEWE44/musicDownload.git
cd musicDownload
python -m venv gqb313
gqb313\Script\Activate.bat
cd musicDownload
pip install -r requirements.txt
python musicdownload.py 
```

### 打包教程：

```
# 需要用Python3.13
git clone https://github.com/MrsEWE44/musicDownload.git
cd musicDownload
python -m venv gqb313
gqb313\Script\Activate.bat
cd musicDownload
pip install -r requirements.txt

# 如果你是Windows系统，运行make_release.bat文件
.\make_release.bat

# 如果你是Linux、MacOS系统，运行make_release.sh文件
bash make_release.sh
```


