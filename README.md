# ほどほどタイピング

速すぎても遅すぎてもいけない、リズムを守るタイピングゲームです。
ブラウザで `hodohodo-typing_credits.html` を開くと遊べます。

## ファイル

| ファイル | 内容 |
|---|---|
| `hodohodo-typing_credits.html` | ゲーム本体(標準の単語リストとクレジット画面を含む) |
| `build_wordlist.py` | 標準単語リストの作成スクリプト |
| `NOTICE.txt` | クレジットとライセンス全文(`build_wordlist.py` が出力。リストを単体で配布するときに同梱) |

## 単語リストの作り方

```
pip install "wordfreq[cjk]"
python build_wordlist.py --wordnet-list words.csv --download
```

- `words.csv` は、日本語WordNetの見出し語を1行1語で並べたものです。XMLから直接作る場合は `--wordnet-xml wnja-2.1.xml` を使います。
- `out/` に次のファイルができます。
  - `typing_words_filtered.csv`(表記,読み)
  - `words_for_game.txt`(ゲームの単語欄に貼れる「よみ,表記」形式)
  - `NOTICE.txt`
  - `build_report.txt`(各段階の語数と、使ったJMdictの版)

### 絞り込みの内容

1. 日本語WordNetの見出し語のうち、漢字・かな・長音だけの語を残す
2. JMdictの一般語(common)と一致する語だけを残し、読み(ひらがな)をJMdictから付ける
3. 読みが2〜10文字で、同じ読みの重複がない語だけを残す
4. JMdictで読みが複数ある語を除く
5. wordfreq の使用頻度(zipf 3.0以上)で絞る
6. 古い語・不適切な語(JMdictの用法タグ)を除く

## JMdict更新手順

JMdictのライセンス(EDRDG、第4条)は、JMdictのデータを使うソフトに、最新版から定期的に更新する手順を持つことを求めています。

**この更新は自動では行われません。** ゲームのHTMLに入っている単語リストは固定のデータで、ゲーム自体がJMdictを取得し直すことはありません。更新は、このプロジェクトの**管理者(開発者)が手動で**行い、更新後のHTMLを公開し直します。ゲームを遊ぶ人が、何かを操作する必要はありません。

**管理者は、毎月1回、次の手順を実行します。**

1. `python build_wordlist.py --wordnet-list words.csv --download` を実行する(JMdictの最新版を取得して作り直す。作業はこの1回の実行だけです)。
2. `out/build_report.txt` に記録された、JMdictの版・日付を確認する。
3. `out/words_for_game.txt` の内容を、ゲームの標準単語リスト(HTML内の `DEFAULT_WORDS`)に反映する。
4. ゲームのクレジット画面と `NOTICE.txt` の、JMdictの版の表記を更新する。
5. 更新したHTMLを公開し直す。

更新した日と、そのときのJMdictの版は、`build_report.txt` と、クレジット画面の「使用版」の表記で確認できます。

## ライセンスとクレジット

- 単語リストは、次のデータをもとに作成・加工した派生データです。**CC BY-SA 4.0** で提供します。
  - JMdict(© James William Breen and EDRDG、CC BY-SA 4.0)
  - 日本語ワードネット(クレジット表記は公式のダウンロードページの指定どおり。ライセンス全文は公式の `license.txt` の原文を、クレジット画面と `NOTICE.txt` に収録)
  - wordfreq(© Robyn Speer。コードは Apache License 2.0、データは CC BY-SA 4.0)
- 本プロジェクトの作者は、これらのデータについて著作権を主張しません。
- 単語リストだけを別に配布するときは、`NOTICE.txt` を必ず同梱してください。

### 公開前の確認

- 日本語ワードネットの**クレジット表記**(「日本語ワードネット （2.1版）© …」とリンク)が、公式の[ダウンロードページ](https://bond-lab.github.io/wnja/eng/downloads.html)の「Note on Licence Compliance」と同じか。
- 日本語ワードネットの**ライセンス全文**が、公式の <https://bond-lab.github.io/wnja/license.txt> の原文と同じか。(著作権の年の行は、この原文のとおりに収録しています。クレジット表記の年とは別です。)
- クレジット画面の、JMdictの版・日付が、最新の `build_report.txt` と合っているか。
