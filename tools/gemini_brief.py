#!/usr/bin/env python3
"""Gemini に渡す説明資料（のんびり牧場の概要・キャラ表・用語集・チェックのお願い）を PDF にする。"""
import json, pathlib, html
from playwright.sync_api import sync_playwright
root = pathlib.Path(__file__).resolve().parent.parent
N = json.loads((root / "i18n" / "en.json").read_text(encoding="utf-8"))["nouns"]
e = html.escape
CHARS = [
 ("みのり", "Minori", "牧場の案内役。亡くなった祖母の牧場を継いだ。畑・事務所の担当。まじめでやさしい。",
  "ていねいな敬語（〜です・〜ますね）。やわらかく、相手を気づかう。",
  "Polite, warm and gentle. Never slangy.", "「お疲れさまです」→ Good work. ／「ありがとうございます。みんな、きっと喜んでいますね」"),
 ("こはく", "Kohaku", "大工だった祖父に育てられた。森の小屋に住んでいた。厩舎・資材・建築の担当。無口。",
  "とても短い言葉。「……」が多い。相手を「あんた」と呼ぶ。そっけないが、根はやさしい。",
  "Very short, blunt sentences with lots of “……”. Calls the player “you” bluntly. Quietly kind.", "「……任せて」→ ……Leave it to me. ／「……悪くない」→ ……Not bad."),
 ("ひなた", "Hinata", "実家の小さな牧場が閉じた過去がある。養鶏・酪農・養蜂の担当。動物に食べ物の名前をつける。",
  "元気いっぱい。「わーい！」「やったー！」「〜だね！」。敬語まじりだが子どもっぽく明るい。",
  "Bubbly and energetic. Lots of “!”. “Yay!” “Let's do our best!”", "「わーい！〜だね！がんばろー！」→ Yay! It's ~! Let's do our best!"),
 ("あかり", "Akari", "元エンジニア。大きな工場で働きすぎて眠れなくなり、牧場に来た。工場・資材の担当。いつも眠そう。",
  "ゆるい語尾「〜っス」「〜っス〜…」。のんびり、だるそう。でも腕は確か。",
  "Laid-back, sleepy, drawn-out endings: “~…”, “got it~…”. Casual but competent.", "「〜っスね〜…了解っス〜…」→ ~, huh~… got it~…"),
 ("つばき", "Tsubaki", "旅館と織物の家のお嬢様。家の旅館が閉じ、家の名を取り戻すと決めている。茶畑・繊維・商業施設の担当。",
  "お嬢様言葉「〜ですわ」「〜ですの」「わたくし」。上品で少し高飛車。ほめるときは照れて否定する（ツンデレ）。",
  "Refined, proper and a little haughty (“I see.” “No slacking, you hear?”). Flustered when praising (tsundere).", "「当然の結果ですわ」→ A natural result, of course. ／「べ、別に褒めていませんわよ」→ I-it's not as if I'm praising you."),
 ("しずく", "Shizuku", "雨の温室にいる無口な少女。言葉が「こわれて」いて、文字化けした文字で話す（わざとの設定）。透明な傘・青い鳥・くまのぬいぐるみ。",
  "文字化けした文字＋（ ）の中に本当の意味。「……」が多い。最終回で一度だけ文字化けせずに話す。",
  "Keep the garbled characters exactly as they are. Translate only the meaning inside （ ）, in short, soft words.", "「……縺ゅａ縲√☆縺�（あめ、すき）」→ ……縺ゅａ縲√☆縺�（rain… I like it）"),
]
GROUPS = [
 ("場所・部門", ["畑","ビニールハウス","田んぼ","果樹園","ガラス温室","茶畑","花卉","養鶏","酪農","養蜂","養蚕","厩舎","鶏小屋","牛小屋","羊小屋","豚小屋","木材","石材","山開拓","採水地","建築","清掃","工場","工房","商業施設","ホームセンター","温泉旅館","飲食店","事務所","総務","人事","営業","物流","投資","耕種","畜産","資材"]),
 ("工場", ["ジュース工場","酒造工場","お茶工場","乳製品工場","繊維工場","精肉工場","天然水工場","薬品工場","工芸品工房","建築現場"]),
 ("作物・製品", ["小麦","じゃがいも","キャベツ","トマト","いちご","米","卵","ミルク","肉","羊毛","はちみつ","生糸","茶葉","果実","ジュース","果実酒","はちみつレモネード","チーズ","毛糸","堆肥","肥料","高品質肥料","飼料","種"]),
 ("人・売り先", ["従業員","日雇いバイト","派遣社員","事務員","店員","道の駅","農協","ネット販売","有名ブランド化","海外へ輸出"]),
]
SYS = [("区画","plot"),("〜P目（ページ）","page"),("ブロック","block"),("棟","building"),("出荷","ship / shipping"),("納品","deliver"),("収穫","harvest"),("増設","expand / add"),("機械化","mechanize"),("一括〜","… (all) / bulk"),("小売販売","Retail"),("持ち場","workplace"),("持ち物","Bag"),("ショップ","Store"),("お願い","request"),("依頼","request"),("出荷イベント","shipping event"),("ストーリー 第N話","story, Ep. N"),("♥（好感度）","♥ (affection)"),("AP","AP"),("Lv.","Lv."),("牧場主","Farm owner"),("季節ノルマ","season quota")]
def table(rows, cols):
    h = "".join(f"<th>{e(c)}</th>" for c in cols)
    b = "".join("<tr>" + "".join(f"<td>{e(x)}</td>" for x in r) + "</tr>" for r in rows)
    return f"<table><tr>{h}</tr>{b}</table>"
gl = ""
for title, keys in GROUPS:
    rows = [(k, N[k]) for k in keys if k in N]
    gl += f"<h3>{e(title)}</h3>" + table(rows, ["日本語", "English"])
gl += "<h3>システム用語</h3>" + table(SYS, ["日本語", "English"])
doc = f"""<!doctype html><meta charset=utf-8><style>
body{{font-family:"Noto Sans CJK JP",sans-serif;font-size:10pt;line-height:1.55;margin:0;color:#222}}
h1{{font-size:17pt;margin:0 0 4px}} h2{{font-size:13pt;border-left:5px solid #8bc34a;padding-left:8px;margin:18px 0 8px}} h3{{font-size:11pt;margin:12px 0 4px}}
table{{border-collapse:collapse;width:100%;margin-bottom:6px}} th,td{{border:1px solid #ccc;padding:3px 6px;vertical-align:top;text-align:left}} th{{background:#f1f6ea}}
.box{{background:#fbf7ec;border:1px solid #e6dcc0;border-radius:6px;padding:8px 12px}} .pb{{page-break-before:always}} .sm{{font-size:9pt;color:#555}}
</style>
<h1>「のんびり牧場」英語版チェックのための説明資料</h1>
<p class=sm>Gemini さんへ：このあと対訳の表（番号つき）をお渡しします。先にこの資料でゲームのことを知っておいてください。</p>

<h2>1. ゲームの概要</h2>
<div class=box>
<p><b>どんなゲーム：</b>スマホやパソコンのブラウザで遊ぶ、のんびりした牧場経営ゲーム（横画面）。畑で作物を育てるところから始めて、家畜・工場・お店・事務所まで、牧場を少しずつ大きくしていきます。従業員を雇って作業をまかせ、季節（春夏秋冬）ごとに育つものが変わります。</p>
<p><b>雰囲気：</b>やさしくて、ほのぼの。急がせたり、あおったりしません。ドット絵の背景に、アニメ調のキャラが6人。それぞれに5話のストーリーがあります。</p>
<p><b>遊ぶ人：</b>海外のインディーゲームサイト itch.io の利用者（英語を読む人）。日本のアニメ風のゲームが好きな人、気軽に遊べる経営ゲームが好きな人。</p>
<p><b>英語の方針：</b>やさしく自然な英語。むずかしい単語は避け、画面がせまいので短く。日本らしい名前（Hojicha, Kimono, Shochu など）はそのまま残します。お金は ¥（円）のまま。</p>
</div>

<h2>2. キャラクター表</h2>
{table([(c[0]+" / "+c[1], c[2], c[3], c[4], c[5]) for c in CHARS], ["名前", "どんな人", "日本語の話し方", "英語での話し方", "訳の例"])}
<p class=sm>※ プレイヤーは「牧場主」（Farm owner）。セリフの中の {{name}} はプレイヤーの名前が入る場所です。<br>
※ 登場する動物の名前（もちこ・きなこ・ごまだんご など）は、ローマ字のまま（Mochiko, Kinako, Gomadango）にします。</p>

<h2 class=pb>3. 用語集（訳をそろえる言葉）</h2>
{gl}

<h2 class=pb>4. Gemini さんにチェックしてほしいこと</h2>
<div class=box>
<ol>
<li><b>誤訳・訳漏れ</b>がないか（意味がちがう、日本語の一部が訳されていない）</li>
<li><b>英語として不自然な表現</b>がないか</li>
<li><b>キャラクターの口調</b>が、2. のキャラクター表の性格と合っているか</li>
<li><b>用語集どおり</b>に訳がそろっているか（同じ言葉が別の訳になっていないか）</li>
</ol>
<p><b>守ってほしいこと</b></p>
<ul>
<li>{{1}} {{2}} などの記号は、数字が入る場所です。消さずに残してください（英語の語順に合わせて場所は動かしてOK）</li>
<li>{{name}} はプレイヤーの名前が入る場所です。そのまま残してください</li>
<li>絵文字、¥、Lv.、♥ はそのまま残してください</li>
<li>しずくの文字化けした文字は、わざとです。直さずにそのまま残し、（ ）の中だけを訳してください</li>
<li>ボタンや吹き出しはせまいので、なるべく短く。今の訳より長くなる直しは、理由があるときだけにしてください</li>
</ul>
<p><b>返し方：</b>問題のある箇所ごとに、次の形で1行ずつ書いてください。問題のない行は書かなくてかまいません。</p>
<p style="font-family:monospace;background:#fff;border:1px dashed #bbb;padding:6px">番号｜元の日本語｜今の英訳｜直した英訳｜理由（ひとこと）</p>
<p class=sm>例：　512｜今日はもう渡しました（また明日）｜Already given today (try again tomorrow)｜Already given today. Try again tomorrow!｜ほかの通知と形をそろえるため</p>
<p>量が多いので、途中で止まったときは「まとまり○から続けて」と言われたら、その続きからお願いします。</p>
</div>
"""
out = root / "i18n" / "gemini" / "gemini_brief.pdf"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = b.new_page(); pg.set_content(doc); pg.pdf(path=str(out), format="A4", margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"})
    b.close()
print(out)
