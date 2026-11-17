# ほどほどタイピング

速すぎても遅すぎてもいけない、リズムを守るタイピングゲームです。

ブラウザで以下のURLにアクセスすると、すぐに遊べます。
**公開URL:** https://jigendaddy.github.io/hodohodo-typing/

## ファイル構成

| ファイル | 内容 |
|---|---|
| `index.html` | ゲーム本体（標準の単語リストとクレジット画面を含む） |
| `build_wordlist.py` | 標準単語リストの作成スクリプト（`out/NOTICE.txt` などのクレジットも同時に出力します） |
| `.github/workflows/update-wordlist.yml` | 単語リストを自動更新するGitHub Actionsの設定 |
| `README.md` | このファイル |

## 単語リストの自動更新について

本プロジェクトでは、JMdict / 日本語WordNet / wordfreq から派生した単語リストを使用しています。
EDRDG（JMdict）のライセンス（第4条）は、データを使うソフトに最新版への追従を求めているため、**GitHub Actionsによる自動更新の仕組み**を導入しています。

**仕組み:**
* 毎月1日（日本時間 9:00）にGitHub Actionsが自動で起動します。
* 最新のJMdict（jmdict-simplified）と日本語WordNetから単語リストを再生成します。
* `build_wordlist.py` を実行して最新の `DEFAULT_WORDS` を生成し、`index.html` に自動で埋め込みます。
* 変更があれば自動的にGitHubへコミット・プッシュされます。

**手動で更新したい場合:**
1. `python build_wordlist.py --wordnet-list words.csv --download` を実行する。
2. 生成された `out/words_for_game.txt` の内容を `index.html` の `DEFAULT_WORDS` に反映する。
3. クレジット画面と `out/NOTICE.txt` の、JMdictの版の表記を更新する。

## 単語リストの作り方（手動実行）

```bash
pip install "wordfreq[cjk]"
python build_wordlist.py --wordnet-list words.csv --download
```
- `words.csv` は、日本語WordNetの見出し語を1行1語で並べたものです。XMLから直接作る場合は `--wordnet-xml wnja-2.1.xml` を使います。
- `out/` に単語リスト（CSV, TXT）や `NOTICE.txt` が出力されます。

### 絞り込みの内容

1. 日本語WordNetの見出し語のうち、漢字・かな・長音だけの語を残す
2. JMdictの一般語(common)と一致する語だけを残し、読み(ひらがな)をJMdictから付ける
3. 読みが2〜10文字で、同じ読みの重複がない語だけを残す
4. JMdictで読みが複数ある語を除く
5. wordfreq の使用頻度(zipf 3.0以上)で絞る
6. 古い語・不適切な語(JMdictの用法タグ)を除く

## ライセンスとクレジット

- 単語リストは、次のデータをもとに作成・加工した派生データです。**CC BY-SA 4.0** で提供します。
  - JMdict（© James William Breen and EDRDG、CC BY-SA 4.0）
  - 日本語ワードネット（© NICT ほか。ライセンス全文はクレジット画面に収録）
  - wordfreq（© Robyn Speer。コードは Apache License 2.0、データは CC BY-SA 4.0）
- 本プロジェクトの作者は、これらのデータについて著作権を主張しません。
- 単語リストだけを別に配布するときは、`build_wordlist.py` が `out/` に出力する `NOTICE.txt` を必ず同梱してください。
