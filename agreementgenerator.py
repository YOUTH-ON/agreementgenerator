import streamlit as st
import requests
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4
from datetime import datetime
import io

# PDF用日本語フォントの設定
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

# --- 住所検索関数 ---
def get_address(zipcode):
    if not zipcode:
        st.warning("郵便番号を入力してください。")
        return None
    url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={zipcode}"
    try:
        response = requests.get(url)
        data = response.json()
        if data['results']:
            res = data['results'][0]
            return f"{res['address1']}{res['address2']}{res['address3']}"
        else:
            st.error("住所が見つかりませんでした。")
            return None
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return None

# --- PDF生成関数 ---
def create_pdf(content):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont('HeiseiKakuGo-W5', 10)
    width, height = A4
    y = height - 50
    for line in content.split('\n'):
        if y < 50:
            p.showPage()
            p.setFont('HeiseiKakuGo-W5', 10)
            y = height - 50
        p.drawString(50, y, line)
        y -= 15
    p.save()
    buffer.seek(0)
    return buffer

st.title("契約書作成アプリ Pro")

# --- セッション状態の初期化（住所保持用） ---
if 'kou_address' not in st.session_state:
    st.session_state.kou_address = ""
if 'otsu_address' not in st.session_state:
    st.session_state.otsu_address = ""

# --- 入力フォーム ---
with st.form("contract_form"):
    st.subheader("基本情報")
    contract_options = ["業務委託", "秘密保持(NDA)", "売買", "賃貸借", "アドバイザリー"]
    contract_type = st.selectbox("契約書種別", contract_options)
    business_name = st.text_input("業務名（例：Webサイト制作業務）")
    
    # ② 報酬単位に「1件当たり報酬額」を追加
    col_reward1, col_reward2, col_reward3 = st.columns([1, 2, 1])
    with col_reward1:
        reward_type = st.selectbox("報酬単位", ["日額", "月額", "年額", "1件当たり報酬額"])
    with col_reward2:
        reward_amount = st.number_input("金額 (円)", min_value=0, step=1000)
    with col_reward3:
        tax_type = st.selectbox("税区分", ["税込", "税抜き"])
    
    payment_condition = st.text_input("入金条件", placeholder="翌月末日")

    # ③ 住所自動入力（甲）
    st.subheader("当事者情報（甲）")
    col_zip_k1, col_zip_k2 = st.columns([2, 1])
    with col_zip_k1:
        kou_zip = st.text_input("甲：郵便番号 (ハイフンなし)", max_chars=7, key="kou_zip_input")
    with col_zip_k2:
        # フォーム内のボタンは少し特殊なため、外で処理するかFormのSubmitを活用するのが一般的ですが、
        # ここでは住所検索用のトリガーとして説明文を添えます。
        st.write(" ") 
        search_kou = st.form_submit_button("甲：住所自動入力")

    if search_kou:
        addr = get_address(kou_zip)
        if addr:
            st.session_state.kou_address = addr
            
    kou_address = st.text_input("甲：所在地", value=st.session_state.kou_address)
    kou_name = st.text_input("甲：名称")
    kou_title = st.text_input("甲：役職・代表者名")

    # ③ 住所自動入力（乙）
    st.subheader("当事者情報（乙）")
    col_zip_o1, col_zip_o2 = st.columns([2, 1])
    with col_zip_o1:
        otsu_zip = st.text_input("乙：郵便番号 (ハイフンなし)", max_chars=7, key="otsu_zip_input")
    with col_zip_o2:
        st.write(" ")
        search_otsu = st.form_submit_button("乙：住所自動入力")

    if search_otsu:
        addr = get_address(otsu_zip)
        if addr:
            st.session_state.otsu_address = addr

    otsu_address = st.text_input("乙：所在地", value=st.session_state.otsu_address)
    otsu_name = st.text_input("乙：名称")
    otsu_title = st.text_input("乙：役職・代表者名")

    contract_date = st.date_input("契約締結日", datetime.now())
    
    # 最終的な契約書生成ボタン
    submit_main = st.form_submit_button("契約書(PDF)を確定・生成")

# --- プレビューとPDF生成 ---
if submit_main:
    reward_text = f"{reward_type} {reward_amount:,}円（{tax_type}）"
    
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
    
    pdf_file = create_pdf(content)
    st.download_button(
        label="PDFをダウンロード",
        data=pdf_file,
        file_name=f"{contract_type}契約書_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )
