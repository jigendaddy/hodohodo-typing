# ほどほどタイピング

速すぎても遅すぎてもいけない、リズムを守るタイピングゲームです。

ブラウザで以下のURLにアクセスすると、すぐに遊べます。
**公開URL:** https://jigendaddy.github.io/hodohodo-typing/

## ファイル構成

| ファイル | 内容 |
|---|---|
| `index.html` | ゲーム本体（標準の単語リストとクレジット画面を含む） |
| `build_wordlist.py` | 標準単語リストの作成スクリプト |
| `.github/workflows/update-wordlist.yml` | 単語リストを自動更新するGitHub Actionsの設定 |
| `NOTICE.txt` | クレジットとライセンス全文（Actionsが自動で出力。単語リストを単体で配布するときに同梱） |
| `build_report.txt` | 使ったJMdictの版と、各段階の語数（Actionsが自動で出力） |
| `README.md` | このファイル |

`NOTICE.txt` と `build_report.txt` は、最初の自動更新（または手動実行）のあとに作られます。

## 単語リストの自動更新について

本プロジェクトでは、JMdict / 日本語WordNet / wordfreq から派生した単語リストを使用しています。
EDRDG（JMdict）のライセンス（第4条）は、データを使うソフトに、最新版から定期的に更新する手順を持つことを求めているため、**GitHub Actionsによる自動更新の仕組み**を導入しています。

単語リストは、ゲーム本体とは別にGitHub Actionsが定期的にJMdictを取得し、そのデータをもとに自動生成・更新します。更新された単語リストはゲーム本体に組み込まれるため、遊ぶ人がJMdictを取得したり、更新操作をしたりする必要はありません。

更新後の標準単語リストは、次回ページを読み込んだときから適用されます。すでにプレイ中の場合は、ページを再読み込みしない限り、読み込み済みの単語リストがそのまま使用されます。

ただし、単語欄を自分で編集した場合は、その内容がブラウザに保存され、以後は標準単語リストよりも優先して使用されます。

**仕組み:**
* 毎月1日（日本時間 9:00）にGitHub Actionsが自動で起動します。手動でも実行できます（Actionsの画面の「Run workflow」）。
* 日本語WordNetのXMLと、JMdictの最新版（jmdict-simplified）を取得し、単語リストを再生成します。
* `build_wordlist.py` が、`index.html` の標準単語リスト（`DEFAULT_WORDS`）と、クレジット画面のJMdictの版・語数を、自動で書き換えます。
* 変更があれば、`index.html`・`NOTICE.txt`・`build_report.txt` をコミットします。変更がなければ、何もしません。

**安全のための仕組み:** 次の場合は、何も書き換えずに、実行を失敗にします。
* 日本語WordNetの取得に失敗した、または見出し語が極端に少ない場合
* 単語リストの語数が5,000語未満の場合
* 単語リストの語数が、現在より30%以上減る場合
* `index.html` の更新箇所が見つからない場合

**管理者がすること:**
* 毎月、Actionsの実行結果（緑のチェックか、赤い×か）を確認してください。失敗していたら、ログを見て原因を直し、手動で再実行してください。
* GitHubは、リポジトリに長期間動きがないと、定期実行を止めることがあります。ときどき、実行されているか確認してください。
* 更新のコミットのあと、ゲームの標準単語リストに、不適切な語が混ざっていないか、ときどき確認してください（絞り込みは、JMdictの用法タグだけに頼っています）。

**手動で更新したい場合:**
```bash
pip install "wordfreq[cjk]"
curl -fL -o wnja-2.1.xml https://github.com/bond-lab/wnja/releases/download/v2.1/wnja-2.1.xml
python build_wordlist.py --wordnet-xml wnja-2.1.xml --download --out out --update-html index.html
```
`--update-html` を付けると、`index.html` の単語リストと、クレジット画面のJMdictの版・語数も、自動で書き換わります。

## 単語リストの作り方（手動実行）

```bash
pip install "wordfreq[cjk]"
python build_wordlist.py --wordnet-xml wnja-2.1.xml --download
```
- 日本語WordNetの見出し語を1行1語で並べたテキストから作る場合は、`--wordnet-list words.csv` を使います。
- `out/` に次のファイルが出力されます。
  - `typing_words_filtered.csv`（表記,読み）
  - `words_for_game.txt`（ゲームの単語欄に貼れる「よみ,表記」形式）
  - `NOTICE.txt`
  - `build_report.txt`

### 絞り込みの内容

1. 日本語WordNetの見出し語のうち、漢字・かな・長音だけの語を残す
2. JMdictの一般語(common)と一致する語だけを残し、読み(ひらがな)をJMdictから付ける
3. 読みが2〜10文字で、同じ読みの重複がない語だけを残す（同じ読みの語は、先に出た1語を残す）
4. JMdictで読みが複数ある語を除く
5. wordfreq の使用頻度(zipf 3.0以上)で絞る
6. 古い語・不適切な語(JMdictの用法タグ)を除く

## ライセンスとクレジット

- 単語リストは、次のデータをもとに作成・加工した派生データです。**CC BY-SA 4.0** で提供します。
  - JMdict（© James William Breen and EDRDG、CC BY-SA 4.0）
  - 日本語ワードネット（© NICT ほか。クレジット表記は公式のダウンロードページの指定どおり。ライセンス全文は公式の `license.txt` の原文を、クレジット画面と `NOTICE.txt` に収録）
  - wordfreq（© Robyn Speer。コードは Apache License 2.0、データは CC BY-SA 4.0）
- 本プロジェクトの作者は、これらのデータについて著作権を主張しません。
- 単語リストだけを別に配布するときは、`NOTICE.txt` を必ず同梱してください。

### 公開前の確認

- 日本語ワードネットの**クレジット表記**（「日本語ワードネット （2.1版）© …」とリンク）が、公式の[ダウンロードページ](https://bond-lab.github.io/wnja/eng/downloads.html)の「Note on Licence Compliance」と同じか。
- 日本語ワードネットの**ライセンス全文**が、公式の <https://bond-lab.github.io/wnja/license.txt> の原文と同じか。（著作権の年の行は、この原文のとおりに収録しています。クレジット表記の年とは別です。）
