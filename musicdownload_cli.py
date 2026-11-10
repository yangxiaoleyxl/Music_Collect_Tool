#!/usr/bin/env python3
"""Command-line MusicDownload.

Search and download through the musicdl library. This entry point does not
import PySide6 or PyQt5, so the Qt window stack is not required.

Requires Python 3.10 or newer. musicdl 2.10.2 uses 3.10 type syntax and
cannot be imported on Python 3.9.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from typing import Any


DEFAULT_SOURCES = "kuwo,kugou"
PLAYLIST_SOURCES = "netease,qq,kuwo,kugou,migu,qianqian"

# Chinese names used by the Qt window, accepted as --sources values.
CN_ALIASES = {
    "苹果音乐": "AppleMusicClient",
    "deezer": "DeezerMusicClient",
    "5sing": "FiveSingMusicClient",
    "jamendo": "JamendoMusicClient",
    "joox": "JooxMusicClient",
    "酷我音乐": "KuwoMusicClient",
    "酷我": "KuwoMusicClient",
    "酷狗音乐": "KugouMusicClient",
    "酷狗": "KugouMusicClient",
    "咪咕音乐": "MiguMusicClient",
    "咪咕": "MiguMusicClient",
    "网易云音乐": "NeteaseMusicClient",
    "网易云": "NeteaseMusicClient",
    "网易": "NeteaseMusicClient",
    "qq音乐": "QQMusicClient",
    "千千音乐": "QianqianMusicClient",
    "千千": "QianqianMusicClient",
    "qobuz": "QobuzMusicClient",
    "soundcloud": "SoundCloudMusicClient",
    "streetvoice": "StreetVoiceMusicClient",
    "汽水音乐": "SodaMusicClient",
    "汽水": "SodaMusicClient",
    "spotify": "SpotifyMusicClient",
    "tidal": "TIDALMusicClient",
}


def display_width(text: str) -> int:
    width = 0
    for char in text:
        width += 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
    return width


def clip(text: str, width: int) -> str:
    text = " ".join(str(text).split())
    if display_width(text) <= width:
        return text
    kept = []
    used = 0
    for char in text:
        char_width = 2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
        if used + char_width > width - 1:
            kept.append("…")
            break
        kept.append(char)
        used += char_width
    return "".join(kept)


def pad(text: str, width: int) -> str:
    shown = clip(text, width)
    return shown + (" " * (width - display_width(shown)))


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "&".join(str(item) for item in value)
    return str(value)


def song_field(song: Any, key: str, default: str = "") -> Any:
    if isinstance(song, dict):
        return song.get(key, default)
    getter = getattr(song, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(song, key, default)


def source_label(source: str) -> str:
    return str(source or "").removesuffix("MusicClient")


def sanitize_filename(filename: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", filename).strip() or "untitled"


def unique_path(path: str) -> str:
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    index = 1
    while True:
        candidate = f"{stem} ({index}){ext}"
        if not os.path.exists(candidate):
            return candidate
        index += 1


def load_musicdl():
    """Import musicdl only when a command actually needs it."""
    try:
        from musicdl.modules.sources import MusicClientBuilder
        from musicdl.musicdl import MusicClient
    except ImportError as exc:
        sys.exit(
            "未安装 musicdl。命令行版只需要这个库，不要安装 PySide6 或 PyQt5。\n"
            "  python3 -m pip install -r requirements-cli.txt\n"
            "需要 Python 3.10 或更高版本。\n"
            f"当前解释器: {sys.version.split()[0]} ({sys.executable})\n"
            f"导入错误: {exc}"
        )
    except TypeError as exc:
        sys.exit(
            "当前 Python 加载不了 musicdl。已安装的 musicdl 2.10.2 使用了 "
            "Python 3.10 的类型写法（例如 str | dict），在 3.9 上导入就会失败。\n"
            f"当前解释器: {sys.version.split()[0]} ({sys.executable})\n"
            "请改用 Python 3.10 及以上，并且只安装命令行依赖：\n"
            "  python3.12 -m pip install -r requirements-cli.txt\n"
            "不要安装 PySide6 或 PyQt5。图形界面那 1GB 左右的 Qt 绑定与下载无关。\n"
            f"导入错误: {exc}"
        )
    return MusicClient, MusicClientBuilder


def registered_sources(builder) -> dict[str, type]:
    return dict(builder.REGISTERED_MODULES)


def resolve_sources(text: str, registry: dict[str, type]) -> list[str]:
    aliases = {}
    for name in registry:
        short = name.removesuffix("MusicClient").lower()
        aliases[short] = name
        aliases[name.lower()] = name
    for label, name in CN_ALIASES.items():
        if name in registry:
            aliases[label.lower()] = name

    if text.strip().lower() == "all":
        return sorted(registry)

    chosen = []
    unknown = []
    for part in text.split(","):
        key = part.strip()
        if not key:
            continue
        name = aliases.get(key.lower())
        if name is None:
            unknown.append(key)
            continue
        if name not in chosen:
            chosen.append(name)
    if unknown:
        available = ", ".join(sorted(name.removesuffix("MusicClient") for name in registry))
        sys.exit(f"未知音乐源: {', '.join(unknown)}\n可用短名: {available}")
    if not chosen:
        sys.exit("请至少指定一个音乐源。")
    return chosen


def build_client(music_client_cls, sources: list[str], limit: int, work_dir: str):
    config = {
        source: {"search_size_per_source": limit, "work_dir": work_dir}
        for source in sources
    }
    return music_client_cls(music_sources=sources, init_music_clients_cfg=config)


def flatten_results(results: Any) -> list[Any]:
    if isinstance(results, dict):
        groups = list(results.values())
    elif isinstance(results, list):
        groups = [results]
    else:
        groups = []

    songs = []
    for group in groups:
        for song in group or []:
            episodes = song_field(song, "episodes", None)
            if episodes:
                songs.extend(episodes)
            else:
                songs.append(song)
    return songs


def parse_picks(text: str, count: int) -> list[int]:
    picks = []
    for part in text.split(","):
        piece = part.strip()
        if not piece:
            continue
        if "-" in piece:
            start_text, end_text = piece.split("-", 1)
            start, end = int(start_text), int(end_text)
            if start > end:
                start, end = end, start
            picks.extend(range(start, end + 1))
        else:
            picks.append(int(piece))

    chosen = []
    for index in picks:
        if index < 1 or index > count:
            sys.exit(f"序号 {index} 超出范围 1..{count}")
        if index not in chosen:
            chosen.append(index)
    if not chosen:
        sys.exit("没有选中任何歌曲。")
    return chosen


FORMAT_EXTS = {
    "mp3": {"mp3"},
    "wav": {"wav", "wave"},
    "flac": {"flac"},
    "m4a": {"m4a", "aac"},
}


def song_ext(song: Any) -> str:
    return as_text(song_field(song, "ext")).lstrip(".").lower()


def song_bytes(song: Any) -> int | None:
    raw = song_field(song, "file_size_bytes", None)
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def title_key(song: Any) -> str:
    name = as_text(song_field(song, "song_name")).casefold()
    name = re.sub(r"[（(][^)）]*[)）]", " ", name)
    name = re.sub(
        r"(cover|live|remix|version|ver\.?|acoustic|instrumental|伴奏|现场|翻唱|纯音乐|原版|合唱)",
        " ",
        name,
        flags=re.IGNORECASE,
    )
    name = re.sub(r"\s+", " ", name).strip()
    return name or as_text(song_field(song, "song_name")).casefold()


def limit_versions(songs: list[Any], versions: int) -> tuple[list[Any], int]:
    if versions <= 0:
        return songs, 0
    kept = []
    seen: dict[str, int] = {}
    skipped = 0
    for song in songs:
        key = title_key(song)
        count = seen.get(key, 0)
        if count >= versions:
            skipped += 1
            continue
        seen[key] = count + 1
        kept.append(song)
    return kept, skipped


def filter_format(songs: list[Any], fmt: str) -> tuple[list[Any], int]:
    allowed = FORMAT_EXTS.get(fmt)
    if not allowed:
        return songs, 0
    kept = [song for song in songs if song_ext(song) in allowed]
    return kept, len(songs) - len(kept)


def filter_size(songs: list[Any], max_mb: float) -> tuple[list[Any], int]:
    if max_mb <= 0:
        return songs, 0
    limit = int(max_mb * 1024 * 1024)
    kept = []
    skipped = 0
    for song in songs:
        size = song_bytes(song)
        if size is not None and size > limit:
            skipped += 1
            continue
        kept.append(song)
    return kept, skipped


def prefer_mp3() -> None:
    """Ask sources that expose a quality ladder to request MP3 before hi-res."""
    try:
        from musicdl.modules.sources import kugou, kuwo, migu, netease, qianqian
        from musicdl.modules.utils import kugouutils, neteaseutils
    except Exception as exc:
        print(f"无法调整音质顺序，仍按音源默认格式下载: {exc}", file=sys.stderr)
        return
    lossy_first = ["standard", "exhigh", "lossless", "hires", "dolby", "sky", "jyeffect", "jymaster"]
    neteaseutils.MUSIC_QUALITIES[:] = lossy_first
    netease.MUSIC_QUALITIES = neteaseutils.MUSIC_QUALITIES
    kugou_order = ("128", "320", "high", "flac", "viper_clear", "viper_atmos", "viper_tape")
    kugouutils.MUSIC_QUALITIES = kugou_order
    kugou.MUSIC_QUALITIES = kugou_order
    kuwo.KuwoMusicClient.MUSIC_QUALITIES[:] = [(320, "mp3"), (22000, "flac")]
    qianqian.QianqianMusicClient.MUSIC_QUALITIES[:] = ["128", "320", "64", "3000"]
    migu.MiguMusicClient.MUSIC_QUALITIES = {
        "LQ": "mp3",
        "PQ": "mp3",
        "HQ": "mp3",
        "SQ": "flac",
        "ZQ": "flac",
        "Z3D": "flac",
        "ZQ24": "flac",
        "ZQ32": "flac",
    }


def print_songs(songs: list[Any]) -> None:
    if not songs:
        print("没有找到歌曲。")
        return

    headers = ["#", "歌曲", "歌手", "专辑", "格式", "大小", "时长", "来源"]
    widths = [4, 28, 16, 18, 6, 10, 8, 14]
    print("  ".join(pad(header, width) for header, width in zip(headers, widths)))
    print("  ".join("-" * width for width in widths))
    for index, song in enumerate(songs, start=1):
        cells = [
            str(index),
            as_text(song_field(song, "song_name")),
            as_text(song_field(song, "singers")),
            as_text(song_field(song, "album")),
            as_text(song_field(song, "ext")).lstrip(".").upper(),
            as_text(song_field(song, "file_size")),
            as_text(song_field(song, "duration")),
            source_label(as_text(song_field(song, "source"))),
        ]
        print("  ".join(pad(cell, width) for cell, width in zip(cells, widths)))
    print(f"\n共 {len(songs)} 条。下载示例: --pick 1  或  --pick 1,3  或  --pick 1-3  或  --all")


def download_songs(client, songs: list[Any]) -> list[Any]:
    grouped: dict[str, list[Any]] = {}
    for song in songs:
        source = song_field(song, "source", "")
        grouped.setdefault(str(source), []).append(song)

    downloaded = []
    for source, items in grouped.items():
        music = client.music_clients.get(source)
        if music is None:
            print(f"跳过未初始化的源: {source}", file=sys.stderr)
            continue
        result = music.download(song_infos=items)
        if result:
            downloaded.extend(result)
    return downloaded


def export_download(song: Any, target_dir: str) -> str | None:
    save_path = as_text(song_field(song, "save_path"))
    if not save_path or not os.path.exists(save_path):
        return None

    song_name = as_text(song_field(song, "song_name", "未知歌曲")) or "未知歌曲"
    singers = as_text(song_field(song, "singers", "未知歌手")) or "未知歌手"
    album = as_text(song_field(song, "album"))
    identifier = as_text(song_field(song, "identifier"))
    ext = os.path.splitext(save_path)[1].lstrip(".")
    if not ext:
        ext = as_text(song_field(song, "ext", "mp3")).lstrip(".") or "mp3"

    parts = [song_name, singers]
    if album:
        parts.append(album)
    if identifier:
        parts.append(identifier)
    base_name = sanitize_filename("-".join(parts))
    audio_path = unique_path(os.path.join(target_dir, f"{base_name}.{ext}"))
    shutil.move(save_path, audio_path)

    lyric_path = os.path.splitext(save_path)[0] + ".lrc"
    if os.path.exists(lyric_path):
        shutil.move(lyric_path, unique_path(os.path.splitext(audio_path)[0] + ".lrc"))
    return audio_path


def make_work_dir() -> str:
    root = os.path.join(os.getcwd(), ".musicdl_temp")
    os.makedirs(root, exist_ok=True)
    return tempfile.mkdtemp(prefix="cli-", dir=root)


def collect(client, kind: str, query: str) -> list[Any]:
    if kind == "playlist":
        results = client.parseplaylist(query)
    else:
        results = client.search(keyword=query)
    return flatten_results(results)


def run_list(args, kind: str) -> None:
    if getattr(args, "format", "any") == "mp3":
        load_musicdl()
        prefer_mp3()
    music_client_cls, builder = load_musicdl()
    sources = resolve_sources(args.sources, registered_sources(builder))
    work_dir = make_work_dir()
    client = build_client(music_client_cls, sources, args.limit, work_dir)
    songs = collect(client, kind, args.query)
    print_songs(songs)
    if not songs:
        sys.exit(1)

    if args.all:
        selected = list(songs)
        selected, dropped_format = filter_format(selected, args.format)
        if args.format != "any":
            print(f"格式 {args.format}: 保留 {len(selected)} 条，跳过 {dropped_format} 条其他格式")
        selected, skipped_versions = limit_versions(selected, args.versions)
        if args.versions > 0 and skipped_versions:
            print(f"同名最多保留 {args.versions} 个版本，跳过 {skipped_versions} 条")
        selected, skipped_size = filter_size(selected, args.max_mb)
        if args.max_mb > 0 and skipped_size:
            print(f"大于 {args.max_mb:g} MB 的文件跳过 {skipped_size} 条")
        if not selected:
            sys.exit("筛选后没有可下载的歌曲。")
    elif args.pick:
        selected = [songs[index - 1] for index in parse_picks(args.pick, len(songs))]
    else:
        return

    target_dir = os.path.abspath(args.out)
    os.makedirs(target_dir, exist_ok=True)
    downloaded = download_songs(client, selected)
    saved = []
    for song in downloaded:
        path = export_download(song, target_dir)
        if path:
            saved.append(path)
    shutil.rmtree(work_dir, ignore_errors=True)

    if not saved:
        sys.exit("下载结束，但没有得到可保存的音频文件。")
    print(f"\n已保存 {len(saved)} 个文件到 {target_dir}")
    for path in saved:
        print(path)


def run_sources(_args) -> None:
    _, builder = load_musicdl()
    registry = registered_sources(builder)
    print(f"{'短名':<16} {'传给 musicdl 的类名'}")
    for name in sorted(registry):
        print(f"{name.removesuffix('MusicClient').lower():<16} {name}")
    print(f"\n共 {len(registry)} 个源。也可以写中文名，例如 酷我,酷狗,网易云,QQ音乐。")
    print("搜索默认源: " + DEFAULT_SOURCES)
    print("歌单默认源: " + PLAYLIST_SOURCES)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="musicdownload_cli.py",
        description="MusicDownload 的命令行入口。只使用 musicdl，不加载 PySide6 / PyQt5。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python3 musicdownload_cli.py sources\n"
            "  python3 musicdownload_cli.py search 周杰伦 --sources kuwo,kugou --limit 5\n"
            "  python3 musicdownload_cli.py download 周杰伦 --sources kuwo --pick 1 --out ./已下载音乐\n"
            "  python3 musicdownload_cli.py download 刀马旦 --sources netease --limit 20 --all --versions 3 --format mp3\n"
            "  python3 musicdownload_cli.py playlist 'https://music.163.com/#/playlist?id=...' --sources netease --all\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sources = sub.add_parser("sources", help="列出当前 musicdl 实际注册的音乐源")
    sources.set_defaults(func=run_sources)

    def add_common(command, default_sources: str, download: bool) -> None:
        command.add_argument("query", help="搜索关键词，或歌单链接")
        command.add_argument(
            "--sources",
            default=default_sources,
            help="逗号分隔的音乐源短名、中文名或 all。默认: %(default)s",
        )
        command.add_argument("--limit", type=int, default=10, help="每个源最多取多少条")
        if download:
            command.add_argument("--out", default="已下载音乐", help="音频和歌词的保存目录")
            command.add_argument("--pick", help="要下载的序号，例如 1,3 或 1-5")
            command.add_argument("--all", action="store_true", help="下载本次列出的结果")
            command.add_argument(
                "--versions",
                type=int,
                default=3,
                help="同一歌名最多下载几个版本。0 表示不限制。默认: %(default)s",
            )
            command.add_argument(
                "--format",
                choices=("any", "mp3", "flac", "wav", "m4a"),
                default="any",
                help="只要这种后缀。mp3 会让网易云、酷狗、酷我、咪咕、千千先请求普通音质。默认: %(default)s",
            )
            command.add_argument(
                "--max-mb",
                type=float,
                default=0,
                help="跳过声明体积大于这个兆字节数的文件。0 表示不限制。",
            )

    search = sub.add_parser("search", help="搜索并打印结果，不下载")
    add_common(search, DEFAULT_SOURCES, download=True)
    search.set_defaults(func=lambda args: run_list(args, "search"), all=False, pick=None)

    download = sub.add_parser("download", help="搜索后按序号或全部下载")
    add_common(download, DEFAULT_SOURCES, download=True)
    download.set_defaults(func=lambda args: run_list(args, "search"))

    playlist = sub.add_parser("playlist", help="解析歌单链接后按序号或全部下载")
    add_common(playlist, PLAYLIST_SOURCES, download=True)
    playlist.set_defaults(func=lambda args: run_list(args, "playlist"))
    return parser


def main(argv: list[str] | None = None) -> None:
    if sys.version_info < (3, 10):
        print(
            f"当前解释器是 Python {sys.version.split()[0]}，musicdl 2.10.2 需要 3.10 及以上。\n"
            f"解释器路径: {sys.executable}\n"
            "图形界面的 PySide6 / PyQt5 不是下载所必需的。请用较新的 Python 安装 requirements-cli.txt。",
            file=sys.stderr,
        )
        # --help must stay available so the usage can be read on Python 3.9.
        if argv is None:
            argv = sys.argv[1:]
        if not any(arg in {"-h", "--help", "sources"} for arg in argv):
            sys.exit(1)
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "limit", None) is not None and args.limit < 1:
        sys.exit("--limit 至少为 1")
    if getattr(args, "all", False) and getattr(args, "pick", None):
        sys.exit("--all 和 --pick 只能选一个")
    if getattr(args, "versions", None) is not None and args.versions < 0:
        sys.exit("--versions 不能小于 0")
    if getattr(args, "max_mb", None) is not None and args.max_mb < 0:
        sys.exit("--max-mb 不能小于 0")
    args.func(args)


if __name__ == "__main__":
    main()
