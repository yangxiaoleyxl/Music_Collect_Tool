#!/usr/bin/env bash
# Walk every author in each language. Same title keeps at most 3 versions.
#
#   cd /Volumes/Work/Ph.D/ResearchTools/musicDownload
#   ./download_by_language.sh
#
# Optional:
#   ./download_by_language.sh ./已下载音乐 0 6
#   FORMAT=mp3 ./download_by_language.sh
#   SOURCE=deezer FORMAT=mp3 ./download_by_language.sh
#
# Arguments:
#   1  output root.          default: ./已下载音乐
#   2  cap per language.     default: 0, meaning walk the whole author list
#   3  search results/author default: 6

set -u

ROOT=${1:-./已下载音乐}
CAP=${2:-0}
EACH=${3:-6}
SOURCE=${SOURCE:-netease}
VERSIONS=${VERSIONS:-3}
FORMAT=${FORMAT:-}
PY=${PY:-./.venv/bin/python}
CLI=${CLI:-./musicdownload_cli.py}

if [[ ! -x "$PY" && ! -f "$PY" ]]; then
  echo "找不到 ${PY}。请在 musicDownload 目录下运行。" >&2
  exit 1
fi

count_audio() {
  find "$1" -type f \( \
    -iname '*.mp3' -o -iname '*.flac' -o -iname '*.m4a' -o \
    -iname '*.wav' -o -iname '*.ogg' -o -iname '*.aac' \
  \) | wc -l | tr -d ' '
}

run_lang() {
  local lang=$1
  shift
  local dir=$ROOT/$lang
  mkdir -p "$dir"
  local query n cmd
  for query in "$@"; do
    n=$(count_audio "$dir")
    if [[ "$CAP" != "0" && "$n" -ge "$CAP" ]]; then
      echo "[$lang] 已有 $n 首，达到上限 ${CAP}"
      break
    fi
    echo "[$lang] 当前 $n 首，作者: $query"
    cmd=("$PY" "$CLI" download "$query" --sources "$SOURCE" --limit "$EACH" --all --versions "$VERSIONS" --out "$dir")
    if [[ -n "$FORMAT" ]]; then
      cmd+=(--format "$FORMAT")
    fi
    "${cmd[@]}" || echo "[$lang] 这一位失败，继续下一位: $query" >&2
  done
  echo "[$lang] 结束，共 $(count_audio "$dir") 首，目录 $dir"
}

# 中文
run_lang zh \
  周杰伦 林俊杰 陈奕迅 薛之谦 邓紫棋 李荣浩 毛不易 许嵩 周深 张杰 \
  华晨宇 王力宏 陶喆 林宥嘉 田馥甄 孙燕姿 梁静茹 蔡依林 张惠妹 萧敬腾 \
  汪苏泷 徐佳莹 李健 赵雷 陈粒 张靓颖 杨宗纬 朴树 告五人 五月天 \
  张学友 刘德华 王菲 那英 谭咏麟 李克勤 陈慧娴 林忆莲 张国荣 罗大佑 \
  李宗盛 周华健 齐秦 伍佰 崔健 许巍 汪峰 陈绮贞 苏打绿 韦礼安 \
  卢广仲 张信哲 周传雄 莫文蔚 谢霆锋 容祖儿 张敬轩 邓丽君 蔡琴 费玉清 \
  刘若英 张韶涵 王心凌 潘玮柏 周兴哲 艾怡良 邵夷贝 房东的猫 花粥 陈雪凝 \
  单依纯 黄霄雲 希林娜依高 张碧晨 袁娅维 谭维维 霍尊 刀郎 降央卓玛 腾格尔

# 英文
run_lang en \
  "The Beatles" Queen Adele "Ed Sheeran" "Taylor Swift" Coldplay \
  "Bruno Mars" "Elvis Presley" "Michael Jackson" "Billie Eilish" Beyoncé \
  Rihanna Eminem "Ariana Grande" "Lady Gaga" "Katy Perry" "The Weeknd" \
  "Justin Bieber" "Dua Lipa" "Olivia Rodrigo" "Harry Styles" "Maroon 5" \
  "Imagine Dragons" "Linkin Park" "Green Day" Nirvana Radiohead Oasis \
  U2 "The Rolling Stones" "David Bowie" "Elton John" "Whitney Houston" \
  "Mariah Carey" "Celine Dion" Madonna Prince "Stevie Wonder" "Bob Dylan" \
  "Bob Marley" "Johnny Cash" "Frank Sinatra" "Ella Fitzgerald" "Louis Armstrong" \
  "Norah Jones" "John Legend" "Sam Smith" Sia Lorde "Lana Del Rey" \
  "Arctic Monkeys" "Foo Fighters" "Red Hot Chili Peppers" Metallica "AC/DC" \
  "Pink Floyd" "Led Zeppelin" "Fleetwood Mac" ABBA "Phil Collins" Sting \
  "Paul McCartney" "George Michael" "Britney Spears" "Christina Aguilera" P!nk \
  "Alicia Keys" Usher "John Mayer" "Shawn Mendes" "Charlie Puth" "Lewis Capaldi" \
  Hozier "Vance Joy" Passenger "Post Malone" "Kendrick Lamar" "Doja Cat" \
  "Calvin Harris" "David Guetta" Avicii "Sam Fender" "The Chainsmokers" "Frank Ocean"

# 德文
run_lang de \
  Rammstein "Herbert Grönemeyer" "Die Ärzte" Nena Cro "Helene Fischer" \
  AnnenMayKantereit "Peter Maffay" "Udo Lindenberg" "Die Toten Hosen" "Tokio Hotel" \
  Kraftwerk Silbermond Juli Clueso "Mark Forster" Lea "Tim Bendzko" \
  "Andreas Bourani" Revolverheld Unheilig Alligatoah Marteria Casper Sido \
  "Sarah Connor" "Lena Meyer-Landrut" "Die Fantastischen Vier" "Fettes Brot" Seeed \
  "Peter Fox" Beatsteaks Madsen "In Extremo" "Subway to Sally" Faun Schandmaul \
  "Saltatio Mortis" "Dietrich Fischer-Dieskau" "Fritz Wunderlich" "Jonas Kaufmann" \
  "Diana Damrau" "Bach Kantaten" "Schubert Lieder" "Beethoven Sinfonien" "Mozart Oper" \
  "Brahms Lieder" "Wagner Oper" "Richard Strauss" "Element of Crime" Tocotronic Blumfeld

# 法文
run_lang fr \
  "Édith Piaf" "Charles Aznavour" Stromae Indila Zaz "Serge Gainsbourg" \
  "Jacques Brel" "Francis Cabrel" Angèle "Vanessa Paradis" "Johnny Hallyday" \
  "Mylène Farmer" "Jean-Jacques Goldman" "Patrick Bruel" "Florent Pagny" "Julien Clerc" \
  "Alain Souchon" "Laurent Voulzy" Renaud "Georges Brassens" "Jacques Dutronc" \
  "Françoise Hardy" "France Gall" Dalida "Joe Dassin" "Michel Sardou" \
  "Daniel Balavoine" Calogero "Christophe Maé" Zazie Louane Vianney \
  "Clara Luciani" Pomme "Christine and the Queens" "Daft Punk" Phoenix Justice \
  "Yann Tiersen" Barbara "Charles Trenet" "Yves Montand" "Gilbert Bécaud" \
  "MC Solaar" Orelsan Nekfeu "Grand Corps Malade" Gims "Aya Nakamura" Dadju \
  Ninho Soprano "Black M" Camille M83 "Véronique Sanson" "Alain Bashung"

# 意大利文
run_lang it \
  "Andrea Bocelli" "Laura Pausini" "Eros Ramazzotti" "Luciano Pavarotti" "Il Volo" \
  "Gianna Nannini" "Vasco Rossi" "Ludovico Einaudi" "Claudio Baglioni" Mina \
  "Adriano Celentano" "Lucio Battisti" "Lucio Dalla" "Fabrizio De André" "Francesco De Gregori" \
  "Antonello Venditti" Zucchero Jovanotti Ligabue "Tiziano Ferro" "Marco Mengoni" \
  Ultimo Måneskin Mahmood Elisa Giorgia "Emma Marrone" "Alessandra Amoroso" Annalisa \
  "Ricchi e Poveri" Nomadi Modà Negramaro "Carmen Consoli" "Fiorella Mannoia" \
  "Mia Martini" "Ornella Vanoni" "Patty Pravo" "Raffaella Carrà" "Toto Cutugno" \
  "Umberto Tozzi" "Riccardo Cocciante" "Paolo Conte" "Ennio Morricone" "Il Divo" \
  "Francesco Guccini" Caparezza "Renato Zero" "Gigi D'Alessio" "Pino Daniele"

# 拉丁文：作曲家、合唱团体和曲名
run_lang la \
  "Ave Maria" Requiem "Te Deum" Miserere "Gregorian chant" "Pange lingua" \
  "Dies Irae" "Salve Regina" "The Tallis Scholars" "Carmina Burana" \
  "Mozart Requiem" "Verdi Requiem" "Allegri Miserere" "Vivaldi Gloria" "Bach Magnificat" \
  "Pergolesi Stabat Mater" "Fauré Requiem" "Hildegard von Bingen" Palestrina "Tomás Luis de Victoria" \
  Byrd Tallis Josquin Ockeghem Dufay "The Sixteen" "King's College Choir" \
  "Oxford Camerata" "Ensemble Organum" Libera "Vienna Boys Choir" "Panis Angelicus" \
  "Ave Verum" "Adeste Fideles" "Ubi Caritas" Lacrimosa "Agnus Dei" Kyrie Sanctus

# 西班牙文
run_lang es \
  Shakira "Luis Fonsi" Rosalía "Enrique Iglesias" "Julio Iglesias" "Paco de Lucía" \
  "Buena Vista Social Club" "Jesse & Joy" Maná "Alejandro Sanz" "Bad Bunny" \
  "J Balvin" "Daddy Yankee" Ozuna Maluma "Nicky Jam" "Karol G" "Becky G" \
  Selena Juanes "Carlos Vives" "Ricardo Arjona" "Luis Miguel" "Marco Antonio Solís" \
  "Vicente Fernández" "Alejandro Fernández" Thalía "Paulina Rubio" "Gloria Estefan" \
  "Ricky Martin" "Camila Cabello" "Sebastián Yatra" Morat Reik "Sin Bandera" \
  "Joaquín Sabina" "Joan Manuel Serrat" "Pablo Alborán" "David Bisbal" Melendi Estopa \
  Mecano "La Oreja de Van Gogh" Amaral "Vetusta Morla" "C. Tangana" "Natalia Lafourcade" \
  "Mon Laferte" "Julieta Venegas" "Café Tacvba" "Soda Stereo" "Gustavo Cerati" \
  "Fito Páez" "Andrés Calamaro" "Mercedes Sosa" "Silvio Rodríguez" "Camarón de la Isla" \
  "Vicente Amigo" Tomatito "Estrella Morente" Buika

echo
echo "各语种数量："
for lang in zh en de fr it la es; do
  echo "  $lang  $(count_audio "$ROOT/$lang")  $ROOT/$lang"
done
