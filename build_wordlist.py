#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ほどほどタイピング 標準単語リスト作成スクリプト

日本語WordNetの見出し語を、JMdict(一般語)と wordfreq(使用頻度)で絞り込み、
タイピングゲーム用の「表記・読み(ひらがな)」リストを作ります。

■ 準備
    pip install "wordfreq[cjk]"
    (JMdictは --download で自動取得できます。標準ライブラリのみ使用)

■ 使い方
    # 日本語WordNetの見出し語リスト(1行1語のテキスト/CSV)から作る
    python build_wordlist.py --wordnet-list words.csv --download

    # 日本語WordNetのXML(wnja-*.xml)から直接作る
    python build_wordlist.py --wordnet-xml wnja-2.1.xml --download

    # 取得済みのJMdictを使う場合(jmdict-simplified の .json / .json.zip)
    python build_wordlist.py --wordnet-list words.csv \
        --jmdict-common jmdict-eng-common-*.json.zip --jmdict-full jmdict-eng-*.json.zip

■ 出力(--out で指定したフォルダ。省略時は ./out)
    typing_words_filtered.csv  表記,読み(ひらがな)
    words_for_game.txt         「よみ,表記」形式(ゲームの単語欄にそのまま貼れる)
    NOTICE.txt                 クレジットとライセンス(リストを単体で配布するときに同梱)
    build_report.txt           各段階の語数と、使ったJMdictの版

■ 更新手順(JMdictの更新に追従するための手順)
    1. 本スクリプトを --download 付きで再実行する(JMdictの最新版を取得して作り直す)
    2. build_report.txt に出るJMdictの版・日付を、ゲームのクレジット画面に書き写す
    3. words_for_game.txt の内容をゲームの標準単語リストに差し替える
    JMdictの更新に合わせて、定期的に(目安:数か月に1回)繰り返してください。

■ ライセンス上の注意
    ・出力リストは JMdict / 日本語WordNet / wordfreq から派生したデータです。
      CC BY-SA 4.0 で公開し、NOTICE.txt のクレジットを必ず添えてください。
    ・これらのデータについて著作権を主張しないでください。
"""
import argparse
import csv
import html
import io
import json
import re
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

# ---- 絞り込みの設定 -------------------------------------------------------
BAD_MISC = {"vulg", "sens", "derog", "X"}   # 不適切な語(JMdictの用法タグ)
OLD_MISC = {"obs", "arch"}                  # 古い語
FREQ_MIN = 3.0                              # wordfreq の zipf 値の下限
MIN_LEN, MAX_LEN = 2, 10                    # 読みの文字数
OK_SURFACE = re.compile(r"^[ぁ-んァ-ヶー一-龥々]+$")
HIRA_ONLY = re.compile(r"^[ぁ-んー]+$")

JMDICT_REPO = "https://github.com/scriptin/jmdict-simplified"

NOTICE = """\
ほどほどタイピング 標準単語リスト クレジット
==========================================

このリストは、次のデータをもとに作成・加工したものです。

[JMdict]
(c) James William Breen and The Electronic Dictionary Research and Development Group (EDRDG)
License: Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)
  https://creativecommons.org/licenses/by-sa/4.0/
  https://www.edrdg.org/edrdg/license.html
  https://www.edrdg.org/wiki/index.php/JMdict-EDICT_Dictionary_Project
Used via jmdict-simplified: {repo}
JMdict version: {jmdict_version}

[Japanese WordNet]
Japanese Wordnet (2.1)
Copyright: 2021-2026 Francis Bond, Takayuki Kuribayashi
Copyright: 2018-2020 Francis Bond
Copyright: 2016-2017 Francis Bond, Takayuki Kuribayashi
Copyright: 2012-2015 Francis Bond
Copyright: 2009-2011 NICT
  https://bond-lab.github.io/wnja/eng/index.html
(下に License 全文)

[wordfreq]
(c) Robyn Speer  (code: Apache License 2.0 / data: CC BY-SA 4.0)
  https://github.com/rspeer/wordfreq
単語の使用頻度による絞り込みに使用。

[加工内容 / Modifications]
- 日本語WordNetの見出し語から、JMdictの一般語(common)と一致する語だけを抽出
- 読みはJMdictのものをひらがなに変換して使用
- 次の語を除外: JMdictで読みが複数ある語 / wordfreqの頻度が低い語 /
  古い語・不適切な語(JMdictの用法タグ) / 同じ読みの重複

[このリストのライセンス]
このリストは CC BY-SA 4.0 のもとで提供されます。
各データの著作権は、それぞれの著作権者に帰属します。
本リストの作成者は、これらのデータについて著作権を主張しません。
データの正確さ・完全さは保証されません。

------------------------------------------------------------------
Japanese WordNet License
------------------------------------------------------------------
Copyright: 2021-2026 Francis Bond, Takayuki Kuribayashi
Copyright: 2018-2020 Francis Bond
Copyright: 2016-2017 Francis Bond, Takayuki Kuribayashi
Copyright: 2012-2015 Francis Bond
Copyright: 2009-2011 NICT

Japanese WordNet

This software and database is being provided to you, the LICENSEE, by
the National Institute of Information and Communications Technology
under the following license.  By obtaining, using and/or copying this
software and database, you agree that you have read, understood, and
will comply with these terms and conditions:

  Permission to use, copy, modify and distribute this software and
  database and its documentation for any purpose and without fee or
  royalty is hereby granted, provided that you agree to comply with
  the following copyright notice and statements, including the
  disclaimer, and that the same appear on ALL copies of the software,
  database and documentation, including modifications that you make
  for internal use or for distribution.

THIS SOFTWARE AND DATABASE IS PROVIDED "AS IS" AND NICT MAKES NO
REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE,
BUT NOT LIMITATION, NICT MAKES NO REPRESENTATIONS OR WARRANTIES OF
MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE
OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL NOT INFRINGE
ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR OTHER RIGHTS.

The name of the National Institute of Information and Communications
Technology may not be used in advertising or publicity pertaining to
distribution of the software and/or database.  Title to copyright in
this software, database and any associated documentation shall at all
times remain with National Institute of Information and Communications
Technology and LICENSEE agrees to preserve same.
"""


def kata2hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)


# ---- 入力の読み込み -------------------------------------------------------
def read_wordnet_list(path):
    """1行1語のテキスト/CSV。先頭列を見出し語とする。"""
    words = []
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            w = line.strip().split(",")[0].strip()
            if w:
                words.append(w)
    return words


def read_wordnet_xml(path):
    """WN-LMF形式のXMLから <Lemma writtenForm="..."> を順に取り出す。"""
    text = Path(path).read_text(encoding="utf-8")
    pat = re.compile(r'<Lemma\b[^>]*?\bwrittenForm="([^"]*)"')
    return [html.unescape(m.group(1)).strip() for m in pat.finditer(text)]


def load_json(path):
    path = Path(path)
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist() if n.endswith(".json"))
            with z.open(name) as f:
                return json.load(io.TextIOWrapper(f, encoding="utf-8"))
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def download_jmdict(dest):
    """jmdict-simplified の最新リリースから、一般語版と全体版を取得する。"""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(JMDICT_REPO + "/releases/latest", method="HEAD")
    with urllib.request.urlopen(req) as r:
        final = r.geturl()
    tag = urllib.parse.unquote(final.rsplit("/tag/", 1)[1])
    base = f"{JMDICT_REPO}/releases/download/{urllib.parse.quote(tag, safe='')}"
    paths = {}
    for key, fname in (("common", f"jmdict-eng-common-{tag}.json.zip"),
                       ("full", f"jmdict-eng-{tag}.json.zip")):
        out = dest / fname
        if not out.exists():
            print(f"ダウンロード中: {fname}", file=sys.stderr)
            urllib.request.urlretrieve(f"{base}/{fname}", out)
        paths[key] = out
    return paths["common"], paths["full"]


# ---- 辞書の索引づくり -----------------------------------------------------
def build_common_index(common):
    """表記(またはかな) -> 読み(ひらがな)のリスト。一般語のみ、不適切・古い語は除く。"""
    index = {}
    for e in common["words"]:
        miscs = [set(s.get("misc", [])) for s in e["sense"]]
        if any(m & BAD_MISC for m in miscs):
            continue
        if all(m & OLD_MISC for m in miscs):
            continue
        kana = e["kana"]
        for k in e.get("kanji", []):
            if not k.get("common"):
                continue
            rs = [kata2hira(x["text"]) for x in kana
                  if x.get("common") and
                  (x.get("appliesToKanji", ["*"]) == ["*"] or
                   k["text"] in x.get("appliesToKanji", []))]
            if rs:
                index.setdefault(k["text"], []).extend(rs)
        for x in kana:
            if x.get("common"):
                index.setdefault(x["text"], []).append(kata2hira(x["text"]))
    return index


def build_all_readings(full):
    """表記 -> 登録されている全ての読み(一般語以外も含む)。読みの揺れの検出に使う。"""
    allr = {}
    for e in full["words"]:
        for k in e.get("kanji", []):
            if set(k.get("tags", [])) & {"sK", "iK"}:
                continue
            for x in e["kana"]:
                if "sk" in x.get("tags", []):
                    continue
                a = x.get("appliesToKanji", ["*"])
                if a == ["*"] or k["text"] in a:
                    allr.setdefault(k["text"], set()).add(kata2hira(x["text"]))
    return allr


# ---- 本体 -----------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="ほどほどタイピング 標準単語リスト作成")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--wordnet-list", help="日本語WordNetの見出し語リスト(1行1語)")
    src.add_argument("--wordnet-xml", help="日本語WordNetのXML(WN-LMF)")
    ap.add_argument("--jmdict-common", help="jmdict-eng-common の .json / .json.zip")
    ap.add_argument("--jmdict-full", help="jmdict-eng の .json / .json.zip")
    ap.add_argument("--download", action="store_true", help="JMdictの最新版を自動取得")
    ap.add_argument("--cache", default="jmdict_cache", help="--download の保存先")
    ap.add_argument("--out", default="out", help="出力フォルダ")
    args = ap.parse_args()

    try:
        from wordfreq import zipf_frequency
    except ImportError:
        sys.exit('wordfreq が必要です: pip install "wordfreq[cjk]"')

    if args.download:
        common_path, full_path = download_jmdict(args.cache)
    elif args.jmdict_common and args.jmdict_full:
        common_path, full_path = args.jmdict_common, args.jmdict_full
    else:
        sys.exit("--download か、--jmdict-common と --jmdict-full を指定してください。")

    words = (read_wordnet_list(args.wordnet_list) if args.wordnet_list
             else read_wordnet_xml(args.wordnet_xml))
    report = []

    def log(msg):
        print(msg)
        report.append(msg)

    common = load_json(common_path)
    jm_version = f"{common.get('version', '?')} / dictDate {common.get('dictDate', '?')}"
    log(f"JMdict(jmdict-simplified): {jm_version}")
    index = build_common_index(common)
    del common

    # 1) 重複除去 + 文字種(漢字・かな・長音のみ)
    words = list(dict.fromkeys(w for w in words if w))
    log(f"日本語WordNet 見出し語(重複除去後): {len(words)}")
    words = [w for w in words if OK_SURFACE.match(w)]
    log(f"文字種OK: {len(words)}")

    # 2) JMdictの一般語と一致 + 読みを付ける(読みの長さ制限・同じ読みは先勝ち)
    rows, seen = [], set()
    matched = 0
    for w in words:
        if w not in index:
            continue
        matched += 1
        rs = list(dict.fromkeys(index[w]))
        r = rs[0]
        if not HIRA_ONLY.match(r) or not (MIN_LEN <= len(r) <= MAX_LEN):
            continue
        if r in seen:
            continue
        seen.add(r)
        rows.append((w, r, len(rs)))
    log(f"JMdict一般語と一致: {matched}")
    log(f"読みの長さ{MIN_LEN}-{MAX_LEN}文字・読みの重複除去後: {len(rows)}")

    # 3) 一般語の中で読みが1つだけの語
    rows = [(w, r) for w, r, n in rows if n == 1]
    log(f"読みが1つだけ(一般語内): {len(rows)}")

    # 4) 使用頻度 + JMdict全体で読みが1つだけ
    full = load_json(full_path)
    allr = build_all_readings(full)
    del full
    kept = []
    for w, r in rows:
        if zipf_frequency(w, "ja") < FREQ_MIN:
            continue
        if len(allr.get(w, {r})) > 1:
            continue
        kept.append((w, r))
    log(f"頻度(zipf>={FREQ_MIN})かつJMdict全体で読みが1つだけ: {len(kept)}  ← 最終")

    # ---- 出力 ----
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "typing_words_filtered.csv", "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f)
        wr.writerow(["表記", "読み"])
        wr.writerows(kept)
    (out / "words_for_game.txt").write_text(
        "\n".join(f"{r},{w}" for w, r in kept) + "\n", encoding="utf-8")
    (out / "NOTICE.txt").write_text(
        NOTICE.format(repo=JMDICT_REPO, jmdict_version=jm_version), encoding="utf-8")
    (out / "build_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"\n出力: {out.resolve()}")


if __name__ == "__main__":
    main()
