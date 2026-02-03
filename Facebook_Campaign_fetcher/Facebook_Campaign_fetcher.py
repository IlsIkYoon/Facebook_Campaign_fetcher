from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.exceptions import FacebookRequestError
from Meta_dataClass import CampaignStats
from typing import List


def do_Facebook_Init(appID, appSecret, accessToken):
    FacebookAdsApi.init(
    app_id=appID,
    app_secret=appSecret,
    access_token=accessToken,
    api_version='v24.0'
    )


def get_my_campaigns(accountID):
    account = AdAccount(accountID)

    fields = [
        Campaign.Field.id,
        Campaign.Field.name,
        Campaign.Field.status,
        Campaign.Field.objective,
        Campaign.Field.daily_budget,
        Campaign.Field.start_time,
    ]

    try:
        metrics = [
            'campaign_name',
            'spend',
            'cost_per_action_type',
            'actions'
            ]


        params = {
        'limit': 10,
        'filtering': [
        {'field': 'effective_status', 'operator': 'IN', 'value': ['ACTIVE']}
        ]
        }

        campaigns = account.get_campaigns(fields=fields, params=params)

        print(f"{'ID':<20} | {'Name':<40} | {'Status':<10}")
        print("-" * 80)

        for campaign in campaigns:
            status = campaign.get(Campaign.Field.status)

            # 🔥 ACTIVE만 Python에서 필터링
            if status != 'ACTIVE':
                continue

            print(
                f"{campaign.get('id'):<20} | "
                f"{campaign.get('name')[:38]:<40} | "
                f"{status:<10}"
            )

    except FacebookRequestError as e:
        print("API Error")
        print("Message :", e.api_error_message())
        print("Code    :", e.api_error_code())
        print("Type    :", e.api_error_type())
        print("TraceID :", e.fbtrace_id)




def get_my_campaigns_with_costs(accountID):
    account = AdAccount(accountID)

    # 캠페인 기본 정보 필드 (Metadata)
    campaign_fields = [
        Campaign.Field.id,
        Campaign.Field.name,
        Campaign.Field.status,
    ]

    # 성과 지표 필드 (Insights/Metrics)
    insight_fields = [
        'spend',
        'cost_per_action_type',
    ]

    try:
        # 1. 서버 사이드 필터링으로 ACTIVE 상태인 캠페인만 Get
        params = {
            'limit': 10,
            'filtering': [
                {'field': 'effective_status', 'operator': 'IN', 'value': ['ACTIVE']}
            ]
        }

        campaigns = account.get_campaigns(fields=campaign_fields, params=params)

        print(f"{'Name':<40} | {'Spend':<10} | {'LP View Cost':<12}")
        print("-" * 70)

        for campaign in campaigns:
            # 2. 각 캠페인 객체에서 인사이트(성과) 조회
            # C++의 campaign->get_insights() 호출과 유사함
            insights = campaign.get_insights(fields=insight_fields, params={
                'date_preset': 'last_30d' # 최근 30일 데이터 기준
            })

            # 초기값 설정 (성과 데이터가 없을 경우 대비)
            spend = "0"
            lp_cost = "0"

            if insights:
                # 리스트의 첫 번째 항목(최근 데이터 집계)을 가져옴
                stat = insights[0]
                spend = stat.get('spend', '0')
                
                # cost_per_action_type 내에서 landing_page_view 필터링
                costs = stat.get('cost_per_action_type', [])
                for item in costs:
                    if item['action_type'] == 'landing_page_view':
                        lp_cost = item['value']
                        break

            # 3. 결과 출력
            name = campaign.get('name', 'N/A')
            print(f"{name[:38]:<40} | {spend:<10} | {lp_cost:<12}")

    except FacebookRequestError as e:
        print("API Error occurred.")
        print("Message :", e.api_error_message())
        print("TraceID :", e.fbtrace_id)


def get_marketing_metrics(accountID):
    account = AdAccount(accountID)

    # 1. 캠페인 설정 (Metadata)
    campaign_fields = [
        Campaign.Field.name,
        Campaign.Field.daily_budget,
    ]

    # 2. 성과 지표 (Insights) - cost_per_action_type 추가
    insight_fields = [
        'actions',
        'ctr',
        'purchase_roas',
        'spend',
        'cost_per_action_type', 
    ]

    try:
        # ACTIVE 캠페인만 서버사이드 필터링
        campaigns = account.get_campaigns(fields=campaign_fields, params={
            'filtering': [{'field': 'effective_status', 'operator': 'IN', 'value': ['ACTIVE']}]
        })

        # 헤더 출력 (A4 용지 출력 시 가독성을 위해 간격 조정)
        print(f"{'Name':<30} | {'Conv':<5} | {'CTR':<7} | {'ROAS':<5} | {'LP Cost':<8} | {'Spend%':<7}")
        print("-" * 85)

        for campaign in campaigns:
            # 어제(yesterday) 데이터 조회
            insights = campaign.get_insights(fields=insight_fields, params={'date_preset': 'yesterday'})
            
            # 변수 초기화 (C++ 스타일)
            conv, ctr, roas, lp_cost, spend_ratio = 0, 0.0, 0.0, 0, 0.0

            if insights:
                stat = insights[0]
                
                # [전환 수]
                actions = stat.get('actions', [])
                conv = next((item['value'] for item in actions if item['action_type'] == 'purchase'), 0)
                
                # [CTR]
                ctr = float(stat.get('ctr', 0.0))

                # [ROAS]
                roas_list = stat.get('purchase_roas', [])
                roas = next((item['value'] for item in roas_list if item['action_type'] == 'purchase'), 0.0)

                # [랜딩페이지 조회 비용] - 핵심 추가 로직
                costs = stat.get('cost_per_action_type', [])
                lp_cost = next((item['value'] for item in costs if item['action_type'] == 'landing_page_view'), 0)

                # [당일 지출비율]
                daily_budget = float(campaign.get('daily_budget', 0))
                spend_yesterday = float(stat.get('spend', 0))
                if daily_budget > 0:
                    spend_ratio = (spend_yesterday / daily_budget) * 100

            name = campaign.get('name', 'N/A')
            # 포맷팅 출력
            print(f"{name[:28]:<30} | {conv:<5} | {ctr:.2f}% | {float(roas):.2f} | {float(lp_cost):>8.0f} | {spend_ratio:>6.1f}%")

    except Exception as e:
        print(f"Error: {e}")


def get_filtered_metrics(accountID):
    account = AdAccount(accountID)

    # 1. 캠페인 리스트 가져오기 (상태 필터 제거 혹은 넓게 설정)
    campaign_fields = [
        Campaign.Field.name,
        Campaign.Field.daily_budget,
    ]

    # 2. 성과 지표 필드
    insight_fields = [
        'actions',
        'ctr',
        'purchase_roas',
        'spend',
        'cost_per_action_type',
    ]

    try:
        # 특정 상태에 구애받지 않고 일단 가져옵니다.
        campaigns = account.get_campaigns(fields=campaign_fields, params={'limit': 50})

        print(f"{'Name':<30} | {'Conv':<5} | {'CTR':<7} | {'ROAS':<5} | {'LP Cost':<8} | {'Spend%':<7}")
        print("-" * 85)

        for campaign in campaigns:
            # 어제 데이터 조회
            insights = campaign.get_insights(fields=insight_fields, params={'date_preset': 'yesterday'})
            
            if not insights:
                continue  # 성과 데이터 자체가 없으면 Skip

            stat = insights[0]
            
            # [랜딩페이지 조회 비용 추출]
            costs = stat.get('cost_per_action_type', [])
            # float로 형변환하여 수치 비교가 가능하게 합니다.
            lp_cost = float(next((item['value'] for item in costs if item['action_type'] == 'landing_page_view'), 0))

            # 🔥 [핵심 조건] 랜딩페이지 비용이 0이면 리스트에서 제외 (C++의 Loop Guard)
            if lp_cost < 0.01:
                continue

            # 나머지 지표 계산 로직
            actions = stat.get('actions', [])
            conv = next((item['value'] for item in actions if item['action_type'] == 'purchase'), 0)
            ctr = float(stat.get('ctr', 0.0))
            roas_list = stat.get('purchase_roas', [])
            roas = next((item['value'] for item in roas_list if item['action_type'] == 'purchase'), 0.0)
            
            daily_budget = float(campaign.get('daily_budget', 0))
            spend_yesterday = float(stat.get('spend', 0))
            spend_ratio = (spend_yesterday / daily_budget * 100) if daily_budget > 0 else 0

            name = campaign.get('name', 'N/A')
            print(f"{name[:28]:<30} | {conv:<5} | {ctr:.2f}% | {float(roas):.2f} | {lp_cost:>8.0f} | {spend_ratio:>6.1f}%")

    except Exception as e:
        print(f"Error: {e}")


def get_fast_metrics(accountID):
    account = AdAccount(accountID)

    # 1. 캠페인 설정 정보 가져오기 (Metadata)
    campaigns = account.get_campaigns(fields=[
        Campaign.Field.id,
        Campaign.Field.name,
        Campaign.Field.daily_budget
    ])
    
    # 2. 계정 레벨에서 모든 성과 데이터 한 번에 가져오기 (Bulk Insight Request)
    all_insights = account.get_insights(
        fields=[
            'campaign_id',
            'actions',
            'ctr',
            'purchase_roas',
            'spend',
            'cost_per_action_type'
        ],
        params={
            'date_preset': 'yesterday', # 어제 데이터 기준
            'level': 'campaign'
        }
    )

    # 3. 빠른 매칭을 위해 딕셔너리로 인덱싱 (C++의 std::unordered_map 역할)
    # Key: campaign_id, Value: insight_object
    insight_map = {item['campaign_id']: item for item in all_insights}

    # 헤더 출력 (A4 가독성 고려)
    print(f"{'Name':<30} | {'Conv':<5} | {'CTR':<7} | {'ROAS':<5} | {'LP Cost':<8} | {'Spend%':<7}")
    print("-" * 85)

    for campaign in campaigns:
        campaign_id = campaign.get('id')
        stat = insight_map.get(campaign_id) # O(1) 탐색

        if not stat:
            continue

        # [핵심] 랜딩페이지 비용 추출 및 0원 필터링 (Loop Guard)
        costs = stat.get('cost_per_action_type', [])
        lp_cost = float(next((item['value'] for item in costs if item['action_type'] == 'landing_page_view'), 0))

        if lp_cost < 0.1:
            continue

        # [나머지 지표 추출]
        # 1. 전환 (Purchase)
        actions = stat.get('actions', [])
        conv = next((item['value'] for item in actions if item['action_type'] == 'purchase'), 0)
        
        # 2. CTR
        ctr = float(stat.get('ctr', 0.0))

        # 3. ROAS (Purchase)
        roas_list = stat.get('purchase_roas', [])
        roas = next((item['value'] for item in roas_list if item['action_type'] == 'purchase'), 0.0)

        # 4. 당일 지출비율 (Spend / Daily Budget)
        daily_budget = float(campaign.get('daily_budget', 0))
        spend_yesterday = float(stat.get('spend', 0))
        spend_ratio = (spend_yesterday / daily_budget * 100) if daily_budget > 0 else 0

        # 결과 출력
        name = campaign.get('name', 'N/A')
        print(f"{name[:28]:<30} | {conv:<5} | {ctr:.2f}% | {float(roas):.2f} | {lp_cost:>8.0f} | {spend_ratio:>6.1f}%")


def fetch_campaign_stats_objects(accountID: str) -> List[CampaignStats]:
    """
    메타 데이터를 수집하여 CampaignStats 객체 리스트를 반환합니다.
    """
    account = AdAccount(accountID)
    
    # [Bulk Fetch] 네트워크 호출 2회로 제한 (C++의 최적화된 I/O 방식)
    campaigns = account.get_campaigns(fields=[
        Campaign.Field.id, 
        Campaign.Field.name, 
        Campaign.Field.daily_budget
    ])
    
    all_insights = account.get_insights(
        fields=['campaign_id', 'actions', 'ctr', 'purchase_roas', 'spend', 'cost_per_action_type'],
        params={'date_preset': 'yesterday', 'level': 'campaign'}
    )
    
    # 해시맵 생성: O(1) 탐색을 위해 id를 key로 지정 (std::unordered_map)
    insight_map = {item['campaign_id']: item for item in all_insights}

    results: List[CampaignStats] = []

    for campaign in campaigns:
        campaign_id = campaign.get('id')
        stat = insight_map.get(campaign_id)
        if not stat: continue

        # [Filtering & Data Extraction]
        # 1. 랜딩페이지 비용 추출 (0원 제외 로직)
        costs = stat.get('cost_per_action_type', [])
        lp_cost = float(next((item['value'] for item in costs if item['action_type'] == 'landing_page_view'), 0.0))
        
        if lp_cost == 0: continue

        # 2. 기타 지표 추출
        actions = stat.get('actions', [])
        conv = int(next((item['value'] for item in actions if item['action_type'] == 'purchase'), 0))
        ctr = float(stat.get('ctr', 0.0))
        
        roas_list = stat.get('purchase_roas', [])
        roas = float(next((item['value'] for item in roas_list if item['action_type'] == 'purchase'), 0.0))
        
        # 3. 지출 비율 계산 (Spend / Budget)
        daily_budget = float(campaign.get('daily_budget', 0))
        spend_yesterday = float(stat.get('spend', 0))
        spend_ratio = round((spend_yesterday / daily_budget * 100), 1) if daily_budget > 0 else 0.0

        # [Object Creation] CampaignStats 인스턴스 생성 및 리스트 추가
        results.append(CampaignStats(
            name=campaign.get('name', 'N/A'),
            conv=conv,
            ctr=ctr,
            roas=roas,
            lp_cost=lp_cost,
            spend_ratio=spend_ratio
        ))

    return results