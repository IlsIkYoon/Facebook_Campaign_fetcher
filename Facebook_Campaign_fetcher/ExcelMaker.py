import pandas as pd
from dataclasses import asdict
from typing import List
from Meta_dataClass import CampaignStats

def export_stats_to_excel(stats_list: List[CampaignStats], filename: str = "campaign_report.xlsx"):
    """
    CampaignStats 리스트를 엑셀 파일로 저장합니다.
    """
    if not stats_list:
        print("there is noData...")
        return

    # 1. 객체 리스트를 딕셔너리 리스트로 변환 (C++의 객체 직렬화와 유사)
    # asdict(obj)는 {'name': '광고A', 'conv': 10, ...} 형태의 dict를 만듭니다.
    dict_list = [asdict(stat) for stat in stats_list]

    # 2. Pandas DataFrame 생성 (메모리상의 데이터 테이블)
    df = pd.DataFrame(dict_list)

    # 3. 컬럼 이름 한글화 (선택 사항: 엑셀에서 보기 좋게 변경)
    column_names = {
        'name': '캠페인 이름',
        'conv': '전환수(구매)',
        'ctr': '클릭률(%)',
        'roas': 'ROAS',
        'lp_cost': '랜딩페이지 조회 비용',
        'spend_ratio': '지출 비율(%)'
    }
    df.rename(columns=column_names, inplace=True)

    try:
        # 4. 엑셀 파일로 저장
        # index=False는 엑셀의 제일 왼쪽 행 번호 열을 생성하지 않겠다는 뜻입니다.
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"성공: 데이터가 '{filename}'에 저장되었습니다.")
        
    except Exception as e:
        print(f"엑셀 저장 중 에러 발생: {e}")

# --- 사용 예시 ---
# sorted_list = sorted(stats_list, key=lambda x: x.lp_cost, reverse=True)
# export_stats_to_excel(sorted_list, "메타_캠페인_성과보고서.xlsx")