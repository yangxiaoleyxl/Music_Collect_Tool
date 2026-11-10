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

The Ultimate Music Downloader: Supports lossless audio downloads, batch downloading, one-click downloads, and playlist downloads.

Enables music search and downloading from major streaming platforms—including Kugou, Kuwo, QQ Music, NetEase Cloud Music, Migu, and others—with full support for downloading lossless audio files.

The window is based on [musicdl](https://github.com/CharlesPikachu/musicdl) and [musicdlgui.py](https://github.com/CharlesPikachu/musicdl/blob/master/examples/musicdlgui/musicdlgui.py). The upstream repository is [MrsEWE44/musicDownload](https://github.com/MrsEWE44/musicDownload).

This copy also has a command-line entry point that does not need PySide6. The CLI requires Python 3.10 or newer.

### Screenshots:

<table align="center" border="0" cellpadding="10">

  <tr>
    <td align="center">
      <img src="images/1.png" width="350"><br>
      <b>Image1</b>
    </td>
    <td align="center">
      <img src="images/2.png" width="350"><br>
      <b>Image2</b>
    </td>
    <td align="center">
      <img src="images/3.png" width="350"><br>
      <b>Image3</b>
    </td>
  </tr>
</table>

### Command line

```bash
git clone <your-repo-url>
cd musicDownload
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-cli.txt

python musicdownload_cli.py search "artist name" --sources netease --limit 5
python musicdownload_cli.py download "artist name" --sources netease --limit 6 --all --versions 3 --format flac --out ./已下载音乐
```

`--versions 3` keeps at most three files for the same title. `--format` accepts `mp3`, `flac`, `wav`, `m4a`, or `any`. For the language batches:

```bash
FORMAT=flac ./download_by_language.sh ./已下载音乐 234
```

The second argument is the cap for each language directory.

### Graphical window

The window needs PySide6 from `requirements.txt`.

### Run Example：

```bash
# Using Python3.13
git clone https://github.com/MrsEWE44/musicDownload.git
cd musicDownload
python -m venv gqb313
gqb313\Script\Activate.bat
cd musicDownload
pip install -r requirements.txt
python musicdownload.py 
```

### Run Release Example：

```
# Using Python3.13
git clone https://github.com/MrsEWE44/musicDownload.git
cd musicDownload
python -m venv gqb313
gqb313\Script\Activate.bat
cd musicDownload
pip install -r requirements.txt

# If You Is Windows , Run make_release.bat
.\make_release.bat

# If You Is Linux、MacOS , Run make_release.sh
bash make_release.sh
```

