import streamlit as st
import requests
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from datetime import datetime
import io

# PDF用日本語フォントの設定 (HeiseiKakuGo-W5 を使用)
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

def get_address(zipcode):
    """郵便番号から住所を取得する関数"""
    url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        res = data['results'][0]
        return f"{res['address1']}{res['address2']}{res['address3']}"
    return ""

def create_pdf(content):
    """テキスト内容をPDF化する関数"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont('HeiseiKakuGo-W5', 10)
    
    # テキストを描画（簡易的な改行処理）
    width, height = A4
    y = height - 50
    for line in content.split('\n'):
        if y < 50: # ページをまたぐ処理（簡易版）
            p.showPage()
            p.setFont('HeiseiKakuGo-W5', 10)
            y = height - 50
        p.drawString(50, y, line)
        y -= 15
        
    p.save()
    buffer.seek(0)
    return buffer

st.title("契約書作成アプリ Pro")

# --- 入力フォーム ---
with st.form("contract_form"):
    st.subheader("基本情報")
    
    # ① 契約書種別の選択
    contract_options = ["業務委託", "秘密保持(NDA)", "売買", "賃貸借", "アドバイザリー"]
    contract_type = st.selectbox("契約書種別", contract_options)
    
    business_name = st.text_input("業務名（例：Webサイト制作業務）")
    
    # ② 報酬額の選択と入力
    col_reward1, col_reward2, col_reward3 = st.columns([1, 2, 1])
    with col_reward1:
        reward_type = st.selectbox("報酬単位", ["日額", "月額", "年額"])
    with col_reward2:
        reward_amount = st.number_input("金額 (円)", min_value=0, step=1000)
    with col_reward3:
        tax_type = st.selectbox("税区分", ["税込", "税抜き"])
    
    payment_condition = st.text_input("入金条件", placeholder="翌月末日")

    # ③ 所在地・住所検索
    st.subheader("当事者情報（甲）")
    kou_zip = st.text_input("甲：郵便番号 (ハイフンなし)", max_chars=7)
    kou_address = st.text_input("甲：所在地", value=get_address(kou_zip) if len(kou_zip) == 7 else "")
    kou_name = st.text_input("甲：名称")
    kou_title = st.text_input("甲：役職・代表者名")

    st.subheader("当事者情報（乙）")
    otsu_zip = st.text_input("乙：郵便番号 (ハイフンなし)", max_chars=7)
    otsu_address = st.text_input("乙：所在地", value=get_address(otsu_zip) if len(otsu_zip) == 7 else "")
    otsu_name = st.text_input("乙：名称")
    otsu_title = st.text_input("乙：役職・代表者名")

    contract_date = st.date_input("契約締結日", datetime.now())
    
    submit_button = st.form_submit_button("契約書を生成")

# --- プレビューとPDF生成 ---
if submit_button:
    # 報酬額の文章化
    reward_text = f"{reward_type} {reward_amount:,}円（{tax_type}）"
    
    # 契約書の内容構築
    content = f"""
{contract_type}契約書

{kou_name}（以下「甲」という）と{otsu_name}（以下「乙」という）とは、甲が発注し乙が受注する業務に関する基本事項を定めるため、次のとおり{contract_type}業務委託契約（以下「本契約」という）を締結する。

（業務概要）
第１条 甲は、乙に{business_name}を発注し、乙はこれを受注し、本件業務の目的を理解して誠実に業務を遂行する。

（報酬等）
第１０条 本件業務に関する報酬額は、{reward_text}とする。
（報酬の支払方法）
第１１条 甲は、各月分の報酬額を{payment_condition}までに乙指定の銀行口座に振り込むことで支払う。

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

    st.success("契約書が生成されました！")
    st.text_area("プレビュー", content, height=300)

    # ④ PDFダウンロード
    pdf_file = create_pdf(content)
    st.download_button(
        label="PDFをダウンロード",
        data=pdf_file,
        file_name=f"{contract_type}契約書_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )
