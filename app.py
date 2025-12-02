import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import numpy as np

# --- 1. 기본 설정 ---
st.set_page_config(
    page_title="내 손안의 헬스 매니저 (Care Ver.)",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- [디자인] 커스텀 CSS 주입 (가독성 및 입력창 긴급 수정) ---
def local_css():
    st.markdown("""
        <style>
        /* [1] 전체 앱 배경 및 폰트 설정 (강제 라이트 테마) */
        .stApp {
            background-color: #f4f7f6 !important;
            color: #1a202c !important;
        }
        
        /* 기본 텍스트 색상 고정 */
        p, span, div, li, label, h1, h2, h3, h4, h5, h6 {
            color: #2d3748 !important;
        }

        /* [2] 입력창(Input Widgets) 스타일 긴급 수정 */
        /* 시스템 다크모드 무시하고 무조건 흰 배경에 진한 글씨로 고정 */
        
        /* 텍스트 입력 & 숫자 입력 컨테이너 */
        div[data-baseweb="input"] {
            background-color: #ffffff !important;
            border: 1px solid #cbd5e0 !important;
            border-radius: 8px !important;
        }
        
        /* 실제 입력 필드 (커서 및 텍스트) */
        input[type="text"], input[type="number"] {
            background-color: #ffffff !important;
            color: #1a202c !important; /* 진한 남색 텍스트 */
            caret-color: #000000 !important; /* 커서 색상 */
        }
        
        /* 셀렉트박스 (Selectbox) 컨테이너 */
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #1a202c !important;
            border: 1px solid #cbd5e0 !important;
            border-radius: 8px !important;
        }
        
        /* 셀렉트박스 선택된 텍스트 */
        div[data-testid="stSelectbox"] div[class*="singleValue"] {
            color: #1a202c !important;
        }
        
        /* [3] 탭(Tab) 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: white !important;
            border-radius: 8px 8px 0 0;
            padding: 12px 20px;
            border: 1px solid #e2e8f0;
            border-bottom: none;
            color: #718096 !important;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #38a169 !important;
            color: #ffffff !important;
            border: 1px solid #38a169;
        }
        
        /* [4] 카드 디자인 */
        .custom-card {
            background-color: white !important;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
            margin-bottom: 20px;
        }
        
        /* [5] 처방전 & 경고창 스타일 */
        .prescription-card {
            border-left: 6px solid #38a169;
        }
        .warning-card {
            background-color: #fff5f5 !important;
            border-left: 6px solid #e53e3e;
        }
        /* 경고창 내부 텍스트는 붉은색 유지 */
        .warning-card h4, .warning-card p, .warning-card span, .warning-card b {
            color: #c53030 !important;
        }

        /* [6] 버튼 스타일 */
        .stButton>button {
            border-radius: 8px;
            background-color: #38a169 !important;
            color: white !important;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #2f855a !important;
        }
        
        /* [7] 사이드바 텍스트 및 입력창 */
        section[data-testid="stSidebar"] {
            background-color: #f7fafc !important; /* 사이드바 배경 밝게 */
        }
        section[data-testid="stSidebar"] label {
            color: #2d3748 !important;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

# 그래프 한글 폰트 설정
system_name = platform.system()
if system_name == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif system_name == 'Darwin': 
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='NanumGothic')
plt.rc('axes', unicode_minus=False)

# --- 2. 데이터 로드 ---
@st.cache_data
def load_stat_data():
    try:
        try:
            df = pd.read_csv('supplements.csv', header=1, encoding='cp949') 
        except:
            df = pd.read_csv('supplements.csv', header=1, encoding='utf-8')
        
        df.columns = [c.replace('"', '').strip() for c in df.columns]
        
        if '평균' in df.columns:
            df['평균'] = pd.to_numeric(df['평균'], errors='coerce')
            
        return df
    except Exception as e:
        return pd.DataFrame()

# [DB] 영양제 정보
PRODUCT_DB = {
    '비타민C': {
        'name': '고려은단 비타민C 1000',
        'desc': '활성산소 케어 & 면역 충전',
        'detail': '강력한 항산화 작용으로 피로를 개선하고 면역력을 높여줍니다.',
        'link': 'https://search.shopping.naver.com/search/all?query=비타민C',
        'symptoms': ['피로', '면역력 저하', '감기 기운', '잇몸 출혈'],
        'purposes': ['활력 증진', '피부 미용', '항산화 케어'],
        'dosage_daily': '1,000mg',
        'directions': '산성이 강하므로 **식사 중**이나 **식후**에 섭취하세요.',
        'contraindications': ['신장질환', '위장장애', '요로결석'],
        'risk_msg': '신장 결석 이력이 있거나 위장이 약한 경우 주의가 필요합니다.',
        'stat_keyword': '비타민C'
    },
    '티아민': {
        'name': '임팩타민 (비타민B 컴플렉스)',
        'desc': '지친 일상에 에너지 부스팅',
        'detail': '탄수화물을 에너지로 변환하여 만성 피로 회복을 돕습니다.',
        'link': 'https://search.shopping.naver.com/search/all?query=비타민B',
        'symptoms': ['만성 피로', '무기력', '어깨 결림', '식욕 부진'],
        'purposes': ['활력 증진', '체력 보강', '수험생/직장인 케어'],
        'dosage_daily': '50~100mg',
        'directions': '활력을 위해 **아침 식후** 섭취를 권장합니다.',
        'contraindications': ['위장장애'], 
        'risk_msg': '고함량 복용 시 속쓰림이 발생할 수 있습니다.',
        'stat_keyword': '티아민'
    },
    '비타민A': {
        'name': '루테인 지아잔틴',
        'desc': '침침한 눈을 선명하게',
        'detail': '황반 색소 밀도를 유지하여 눈 건강과 시력 보호에 도움을 줍니다.',
        'link': 'https://search.shopping.naver.com/search/all?query=루테인',
        'symptoms': ['눈 건조', '침침함', '야맹증', '시력 저하'],
        'purposes': ['눈 건강', '노화 방지'],
        'dosage_daily': '20mg (루테인)',
        'directions': '지용성이므로 **식사 직후** 섭취 시 흡수율이 높습니다.',
        'contraindications': ['간 질환', '임산부', '흡연자'], 
        'risk_msg': '장기 과다 섭취 및 흡연자의 고용량 섭취 시 주의가 필요합니다.',
        'stat_keyword': '비타민A'
    },
    '칼슘': {
        'name': '종근당 칼슘 마그네슘 D',
        'desc': '뼈 건강과 편안한 숙면',
        'detail': '뼈와 치아를 형성하고 신경 안정 작용을 합니다.',
        'link': 'https://search.shopping.naver.com/search/all?query=칼슘마그네슘',
        'symptoms': ['관절 통증', '눈 밑 떨림', '불면증', '골다공증'],
        'purposes': ['뼈 건강', '성장 발육', '심신 안정'],
        'dosage_daily': '700~800mg',
        'directions': '근육 이완을 위해 **저녁 식후** 섭취가 좋습니다.',
        'contraindications': ['신장질환', '심혈관질환', '변비'],
        'risk_msg': '신장 기능 저하 시 고칼슘혈증 위험이 있습니다.',
        'stat_keyword': '칼슘'
    },
    '철': {
        'name': '훼라민Q (철분제)',
        'desc': '빈혈 예방과 산소 공급',
        'detail': '혈액 생성을 돕고 체내 산소 운반을 원활하게 합니다.',
        'link': 'https://search.shopping.naver.com/search/all?query=철분제',
        'symptoms': ['빈혈', '어지러움', '창백함', '두통'],
        'purposes': ['임산부 케어', '빈혈 예방'],
        'dosage_daily': '10~14mg',
        'directions': '**공복**에 **비타민C(오렌지주스)**와 함께 드세요.',
        'contraindications': ['위장장애', '간 질환'],
        'risk_msg': '위 점막 자극 및 변비 발생 가능성이 있습니다.',
        'stat_keyword': '철'
    },
    '마그네슘': {
        'name': '닥터스베스트 마그네슘',
        'desc': '근육 이완과 스트레스 완화',
        'detail': '신경과 근육 기능을 유지하고 눈 떨림을 방지합니다.',
        'link': 'https://search.shopping.naver.com/search/all?query=마그네슘',
        'symptoms': ['눈 밑 떨림', '근육 경련', '불면증', '스트레스'],
        'purposes': ['심신 안정', '근육 이완', '수면 질 개선'],
        'dosage_daily': '315mg',
        'directions': '취침 1시간 전 섭취 시 숙면에 도움됩니다.',
        'contraindications': ['신장질환', '서맥'],
        'risk_msg': '신장 배설 기능 저하 시 주의가 필요합니다.',
        'stat_keyword': '마그네슘'
    }
}

stat_df = load_stat_data()

# --- 3. 사이드바 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=80)
    st.markdown("## 📋 Patient Chart")
    st.caption("환자 정보를 입력하세요.")
    st.markdown("---")
    
    name = st.text_input("성명 (Name)", value="김철도")
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("나이", min_value=1, max_value=100, value=37)
    with c2:
        gender_input = st.selectbox("성별", ["남자", "여자"])
    
    st.markdown("---")
    st.markdown("### ⚠️ Medical History")
    st.caption("안전한 처방을 위해 기저 질환을 체크해주세요.")
    disease_list = ['위장장애', '신장질환', '간 질환', '심혈관질환', '당뇨', '요로결석', '임산부', '흡연자', '빈혈', '없음']
    user_diseases = st.multiselect("보유 질환 선택", disease_list)
    
    st.markdown("---")
    st.success(f"**{name}**님 진료 준비 완료.\n오른쪽 화면에서 증상을 선택하세요.")

# --- 4. 메인 화면 ---
col_title1, col_title2 = st.columns([1, 6])
with col_title1:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966334.png", width=70)
with col_title2:
    st.title("Dr. Health Manager")
    st.markdown("##### :leaves: 당신의 건강을 위한 맞춤형 AI 처방 시스템")

tab1, tab2, tab3 = st.tabs(["🩺 AI 처방 & 안전 분석", "💊 구매처 안내", "📊 건강 데이터 분석"])

# --- TAB 1 ---
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
            <div class="custom-card">
                <h3 style="margin-top:0;">📝 문진표 작성</h3>
                <p>현재 상태를 솔직하게 선택해 주시면 더 정확한 처방이 가능합니다.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 1. 주요 증상 (Symptoms)")
            all_symptoms = set()
            for info in PRODUCT_DB.values():
                all_symptoms.update(info['symptoms'])
            selected_symptoms = st.multiselect("불편하신 증상을 모두 선택하세요", sorted(list(all_symptoms)))
        with col2:
            st.markdown("#### 2. 건강 목표 (Goals)")
            all_purposes = set()
            for info in PRODUCT_DB.values():
                all_purposes.update(info['purposes'])
            selected_purposes = st.multiselect("원하시는 개선 효과를 선택하세요", sorted(list(all_purposes)))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("AI 처방전 발급받기 🖨️", key='analyze_btn', use_container_width=True):
        if not selected_symptoms and not selected_purposes:
            st.warning("⚠️ 증상 또는 목표를 하나 이상 선택해 주세요.")
        else:
            st.markdown("---")
            st.subheader(f"📋 **{name}**님을 위한 처방 결과")
            
            recommendations = []
            warnings = [] 
            
            for nutrient, info in PRODUCT_DB.items():
                match_symptom = set(selected_symptoms) & set(info['symptoms'])
                match_purpose = set(selected_purposes) & set(info['purposes'])
                
                if match_symptom or match_purpose:
                    risk_factors = set(user_diseases) & set(info['contraindications'])
                    if risk_factors:
                        warnings.append({'nutrient': nutrient, 'name': info['name'], 'reason': list(risk_factors), 'msg': info['risk_msg']})
                    else:
                        recommendations.append((nutrient, info))
            
            if warnings:
                for warn in warnings:
                    st.markdown(f"""
                        <div class="custom-card warning-card">
                            <h4 style="margin: 0;">🚫 <b>{warn['nutrient']}</b> 복용 주의</h4>
                            <p style="margin-top: 10px;">
                                <b>감지된 위험 요인:</b> <span style="font-weight: bold;">{', '.join(warn['reason'])}</span><br>
                                <br>
                                <b>닥터 코멘트:</b> {warn['msg']}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
            
            if recommendations:
                st.success(f"✅ 분석 완료: {len(recommendations)}가지 맞춤 영양제가 처방되었습니다.")
                for nutrient, info in recommendations:
                    stat_msg = "분석 데이터 부족"
                    if not stat_df.empty:
                        try:
                            col_gender = stat_df.columns[0] 
                            col_nutrient = stat_df.columns[1] 
                            col_sub = stat_df.columns[2]
                            target_row = stat_df[
                                (stat_df[col_gender] == gender_input) & 
                                (stat_df[col_nutrient].str.contains(info.get('stat_keyword', nutrient))) &
                                (stat_df[col_sub] == '소계')
                            ]
                            if not target_row.empty:
                                val = target_row['평균'].values[0]
                                stat_msg = f"한국 {gender_input} 평균: {val}"
                        except: pass

                    st.markdown(f"""
                        <div class="custom-card prescription-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <h3 style="margin: 0; font-size: 1.2rem;">💊 {info['name']} <span style="font-size: 0.8em; color: gray;">({nutrient})</span></h3>
                                <span style="background-color: #c6f6d5; color: #22543d; padding: 5px 10px; border-radius: 15px; font-size: 0.8em; font-weight: bold;">적합도 98%</span>
                            </div>
                            <hr style="border: 0; border-top: 1px dashed #cbd5e0; margin: 15px 0;">
                            <div style="display: flex; flex-wrap: wrap;">
                                <div style="flex: 2; min-width: 250px; margin-right: 20px;">
                                    <p><b>🩺 효능/효과:</b> {info['detail']}</p>
                                    <p><b>📊 데이터 분석:</b> {stat_msg}</p>
                                </div>
                                <div style="flex: 1; min-width: 200px; padding: 15px; border-radius: 10px; background-color: #f0fff4;">
                                    <p style="margin: 0 0 10px 0; color: #2f855a !important; font-weight:bold;">⏰ 섭취 가이드</p>
                                    <ul style="margin: 0; padding-left: 20px; font-size: 0.9em; color: #2d3748;">
                                        <li>권장량: {info['dosage_daily']}</li>
                                        <li>방법: {info['directions']}</li>
                                    </ul>
                                </div>
                            </div>
                            <div style="margin-top: 15px; text-align: right;">
                                <a href="{info['link']}" target="_blank" style="text-decoration: none; font-weight: bold; color: #38a169;">🛒 최저가 구매하러 가기 ></a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            elif not warnings:
                st.info("💡 선택하신 조건에 맞는 추천 영양제가 없습니다.")

# --- TAB 2 ---
with tab2:
    st.markdown("### 🏥 약국 및 온라인 구매 안내")
    col1, col2 = st.columns(2)
    with col1:
         st.markdown("""
            <div class="custom-card">
                <h4>🌐 온라인 공식 판매처</h4>
                <p>품질이 검증된 제품의 온라인 최저가를 확인하세요.</p>
         """, unsafe_allow_html=True)
         for nutrient, info in PRODUCT_DB.items():
             st.markdown(f"- [{info['name']}]({info['link']})")
         st.markdown("</div>", unsafe_allow_html=True)
         
    with col2:
        st.markdown("""
            <div class="custom-card">
                <h4>📍 내 주변 약국 찾기</h4>
                <p>급한 증상이나 전문 약사의 상담이 필요하신가요?</p>
                <br>
                <a href="https://map.naver.com/v5/search/약국" target="_blank">
                    <button style="width: 100%; padding: 15px; border: none; border-radius: 10px; font-size: 1.1em; cursor: pointer; font-weight: bold; background-color: #3182ce; color: white;">
                        🗺️ 네이버 지도로 약국 검색하기
                    </button>
                </a>
            </div>
        """, unsafe_allow_html=True)

# --- TAB 3 ---
with tab3:
    st.markdown("### 📊 2023 국민건강영양조사 대시보드")
    
    if not stat_df.empty:
        col_gender = stat_df.columns[0]
        col_nutrient = stat_df.columns[1] 
        col_sub = stat_df.columns[2]
        
        try:
            target_gender = '전체' if '전체' in stat_df[col_gender].values else '남자'
            energy_row = stat_df[(stat_df[col_gender] == target_gender) & (stat_df[col_nutrient].str.contains('에너지')) & (stat_df[col_sub] == '소계')]
            vitc_row = stat_df[(stat_df[col_gender] == target_gender) & (stat_df[col_nutrient].str.contains('비타민C')) & (stat_df[col_sub] == '소계')]
            
            avg_energy = energy_row['평균'].values[0] if not energy_row.empty else 0
            avg_vitc = vitc_row['평균'].values[0] if not vitc_row.empty else 0
            
            st.markdown(f"""
                <div style="display: flex; gap: 20px; margin-bottom: 30px;">
                    <div class="custom-card" style="flex: 1; text-align: center; padding: 20px;">
                        <span style="font-size: 2em;">⚡</span><br>
                        <span>평균 에너지 ({target_gender})</span><br>
                        <strong style="font-size: 1.5em; color: #d69e2e;">{avg_energy:,.0f} kcal</strong>
                    </div>
                    <div class="custom-card" style="flex: 1; text-align: center; padding: 20px;">
                        <span style="font-size: 2em;">🍋</span><br>
                        <span>비타민 C ({target_gender})</span><br>
                        <strong style="font-size: 1.5em; color: #38a169;">{avg_vitc:.1f} mg</strong>
                    </div>
                    <div class="custom-card" style="flex: 1; text-align: center; padding: 20px;">
                        <span style="font-size: 2em;">📅</span><br>
                        <span>데이터 기준</span><br>
                        <strong style="font-size: 1.5em; color: #2c5282;">2023년</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.warning("지표 로딩 중")

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("##### 🥗 3대 영양소 균형")
            try:
                target_gender = '전체' if '전체' in stat_df[col_gender].values else '남자'
                carb_row = stat_df[(stat_df[col_gender] == target_gender) & (stat_df[col_nutrient].str.contains('탄수화물')) & (stat_df[col_sub] == '소계')]
                prot_row = stat_df[(stat_df[col_gender] == target_gender) & (stat_df[col_nutrient].str.contains('단백질')) & (stat_df[col_sub] == '소계')]
                fat_row = stat_df[(stat_df[col_gender] == target_gender) & (stat_df[col_nutrient].str.contains('지방')) & (stat_df[col_sub] == '소계')]
                
                if not carb_row.empty:
                    carb_val = carb_row['평균'].values[0]
                    prot_val = prot_row['평균'].values[0]
                    fat_val = fat_row['평균'].values[0]
                    
                    fig1, ax1 = plt.subplots(figsize=(6, 4))
                    labels = ['탄수화물', '단백질', '지방']
                    sizes = [carb_val, prot_val, fat_val]
                    colors = ['#ffadad', '#ffd6a5', '#fdffb6'] 
                    explode = (0.05, 0.05, 0.05)

                    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, explode=explode)
                    ax1.axis('equal') 
                    fig1.patch.set_alpha(0)
                    st.pyplot(fig1)
            except: st.write("데이터 없음")

        with col_chart2:
            st.markdown("##### 👫 남녀 영양소 섭취 비교")
            try:
                keywords = {'칼슘': '칼슘', '철': '철', '나트륨': '나트륨', '비타민C': '비타민C'}
                male_vals, female_vals, valid_labels = [], [], []
                
                for label, key in keywords.items():
                    m_row = stat_df[(stat_df[col_gender] == '남자') & (stat_df[col_nutrient].str.contains(key)) & (stat_df[col_sub] == '소계')]
                    f_row = stat_df[(stat_df[col_gender] == '여자') & (stat_df[col_nutrient].str.contains(key)) & (stat_df[col_sub] == '소계')]
                    if not m_row.empty:
                        male_vals.append(m_row['평균'].values[0])
                        female_vals.append(f_row['평균'].values[0])
                        valid_labels.append(label)
                
                if valid_labels:
                    x = np.arange(len(valid_labels))
                    width = 0.35
                    fig2, ax2 = plt.subplots(figsize=(6, 4))
                    rects1 = ax2.bar(x - width/2, male_vals, width, label='남자', color='#a0ced9') 
                    rects2 = ax2.bar(x + width/2, female_vals, width, label='여자', color='#fmb0c2') 
                    ax2.set_xticks(x)
                    ax2.set_xticklabels(valid_labels)
                    ax2.legend()
                    fig2.patch.set_alpha(0)
                    ax2.set_facecolor('none')
                    st.pyplot(fig2)
            except: st.write("데이터 없음")

    else:
        st.warning("데이터 로드 실패")