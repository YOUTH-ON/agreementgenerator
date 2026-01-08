import streamlit as st
from datetime import datetime

# アプリのタイトル
st.title("契約書作成アプリ")
st.write("ひな形に基づいた情報を入力して、契約書を生成します。")

# 入力フォーム
with st.form("contract_form"):
    st.subheader("基本情報")
    contract_type = st.text_input("契約書種別名", placeholder="業務委託")
    business_name = st.text_input("業務名", placeholder="Webサイト制作業務")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("契約期間（始期）", datetime.now())
        reward_amount = st.text_input("報酬額", placeholder="月額 〇〇円（税込）")
    with col2:
        end_date = st.date_input("契約期間（末期）", datetime.now())
        payment_condition = st.text_input("入金条件", placeholder="翌月末日")

    st.subheader("当事者情報（甲）")
    kou_name = st.text_input("甲：名称（会社名など）")
    kou_address = st.text_input("甲：所在地")
    kou_title = st.text_input("甲：役職・代表者名")

    st.subheader("当事者情報（乙）")
    otsu_name = st.text_input("乙：名称（会社名など）")
    otsu_address = st.text_input("乙：所在地")
    otsu_title = st.text_input("乙：役職・代表者名")

    contract_date = st.date_input("契約締結日", datetime.now())

    submit_button = st.form_submit_button("契約書を生成する")

# 契約書テンプレートの適用
if submit_button:
    template = f"""
{contract_type}契約書

{kou_name}（以下「甲」という）と{otsu_name}（以下「乙」という）とは、甲が発注し乙が受注する業務に関する基本事項を定めるため、次のとおり{contract_type}業務委託契約（以下「本契約」という）を締結する。

（業務概要）
第１条 甲は、乙に{business_name}（以下「本件業務」という。）を発注し、乙はこれを受注し、本件業務の目的を理解して誠実に業務を遂行する。

（契約期間）
第２条 甲が本件業務を乙に委託する期間は、{start_date.strftime('%Y年%m月%d日')}から{end_date.strftime('%Y年%m月%d日')}までとする。なお、期間満了の３ヶ月前迄に文書をもって、甲又は乙の双方又は、いずれか一方より改廃の意思表示がない場合には、更に１年間更新し、以後も同様とする。

（中略：第3条〜第9条は共通条項として保持）

（報酬等）
第１０条 本件業務に関する報酬額は、{reward_amount}とする。なお、発注書に定める報酬額が本契約書に定める報酬額より高い場合は、発注書の定めによるものとする。
①個別業務に関する報酬額は個別契約に定める。
②交通費、通信費等諸経費の取り扱いについては、甲乙協議の上、決定する。

（報酬の支払方法）
第１１条 甲は、乙から本件業務を行った月の翌月５日迄に提出を受けた請求書に関し、各月分の報酬額を{payment_condition}までに乙指定の銀行口座に振り込むことで支払う。なお、その際の振込手数料は、甲の負担とする。

（中略：第12条〜第17条は共通条項として保持）

（契約締結の方法）
第１８条 甲と乙は、末尾記載の日付をもって本契約が成立した証として、本電子契約ファイル（以下「本ファイル」という）を作成し、甲乙それぞれ電子署名を行う。

{contract_date.strftime('%Y年%m月%d日')}

（甲）
所在地：{kou_address}
名称：{kou_name}
役職・氏名：{kou_title}

（乙）
所在地：{otsu_address}
名称：{otsu_name}
役職・氏名：{otsu_title}
"""

    st.subheader("プレビュー")
    st.text_area("生成されたテキスト", template, height=400)
    
    # ダウンロードボタン
    st.download_button(
        label="テキストファイルとして保存",
        data=template,
        file_name=f"{contract_type}契約書_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )