from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.exceptions import FacebookRequestError
from facebook_business.api import FacebookAdsApi, FacebookAdsApiBatch
from numpy import isin
from Meta_dataClass import CampaignStats
from typing import List
from facebook_business.adobjects.adcreative import AdCreative


import json


def do_Facebook_Init(appID, appSecret, accessToken):
    FacebookAdsApi.init(
    app_id=appID,
    app_secret=appSecret,
    access_token=accessToken,
    api_version='v24.0'
    )

def get_All_Insight(account):
    """
    meta에 요청해 인사이트를 가져옴. 함수 내부에 가져오는 기준이 있음
    """
    return account.get_insights(
        fields=['campaign_id', 'actions', 'ctr', 'purchase_roas', 'spend', 'cost_per_action_type'],
        params={'date_preset': 'yesterday', 'level': 'campaign'}
    )

def get_All_Campaigns(account):
    """
    meta에 요청해 캠페인을 가져옴. 함수 내부에 가져오는 기준이 있음
    """
    return account.get_campaigns(fields=[
        Campaign.Field.id, 
        Campaign.Field.name, 
        Campaign.Field.daily_budget
    ])

def get_filtered_stats(campaigns, insight_map, video_id_map, video_map) -> List[CampaignStats]:
    results: List[CampaignStats] = []

    print(f"DEBUG: 전체 캠페인 수: {len(campaigns)}")

    for campaign in campaigns:
        campaign_id = campaign.get('id')
        stat = insight_map.get(campaign_id)
        if not stat: continue

        # [Filtering & Data Extraction]
        # 1. 랜딩페이지 비용 추출 (0원 제외 로직)
        costs = stat.get('cost_per_action_type', [])
        lp_cost = float(next((item['value'] for item in costs if item['action_type'] == 'landing_page_view'), 0.0))
        
        if lp_cost < 0.1: continue

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

        # [2. 비디오 URL 매핑 - 전달받은 맵에서 O(1)로 조회]
        video_url = ""
        v_id = video_id_map.get(campaign_id) # 캠페인 ID로 비디오 ID 찾기
        if v_id and v_id in video_map:       # 비디오 ID로 URL 찾기
            video_url = video_map[v_id]


        # [Object Creation] CampaignStats 인스턴스 생성 및 리스트 추가
        results.append(CampaignStats(
            name=campaign.get('name', 'N/A'),
            conv=conv,
            ctr=ctr,
            roas=roas,
            lp_cost=lp_cost,
            spend_ratio=spend_ratio,
            video_url=video_url
        ))


    return results


def fetch_campaign_stats_objects(accountID: str) -> List[CampaignStats]:
    """
    메타 데이터를 수집하여 CampaignStats 객체 리스트를 반환
    """
    account = AdAccount(accountID)

    campaigns_cursor = get_All_Campaigns(account)
    campaigns = list(campaigns_cursor)
    AnalyzeMetaHeader(campaigns_cursor)

    all_insights = list(get_All_Insight(account))
    insight_map = {item['campaign_id']: item for item in all_insights}

    survivors = Filter_Zero_lp_cost(campaigns, insight_map)
    print(f"🔎 [DEBUG 1] 필터링 통과 캠페인: {len(survivors)}개")
    
    video_map = {}
    if survivors:
        #video_id_map = get_Video_IDs_Only_For_Survivors(survivors)
        video_id_map = get_Video_IDs_Only_For_Survivors_test(survivors, account)
        print(f"🔎 [DEBUG 2] 비디오 ID 매핑 완료: {len(video_id_map)}개 캠페인")

        video_map = get_Video_Urls_Batch_Optimized(list(video_id_map.values()))
        print(f"🔎 [DEBUG 3] 실제 URL 수집 완료: {len(video_map)}개 영상")

    #video_map = get_Video_Urls_Batch(campaigns)
    
    return get_filtered_stats(survivors, insight_map, video_id_map, video_map)


def get_Video_Urls_Batch(campaigns) -> dict:
    """
    모든 캠페인에서 비디오 ID를 추출하여 배치로 URL을 수집함 (모듈화)
    """
    video_url_map = {}
    batch = FacebookAdsApiBatch(FacebookAdsApi.get_default_api())
    
    # 1. 중복 없는 비디오 ID 세트 수집 (C++의 std::set과 유사)
    unique_video_ids = set()
    for campaign in campaigns:
        ads_data = campaign.get('ads')
        if ads_data and 'data' in ads_data:
            for ad in ads_data['data']:
                v_id = ad.get('creative', {}).get('video_id')
                if v_id: unique_video_ids.add(v_id)

    # 2. 배치 콜백 정의 (C++의 Lambda Callback)
    def video_callback(response, v_id):
        if not response.error():
            video_url_map[v_id] = response.json().get('source', '')

    # 3. 배치 요청 예약
    for v_id in unique_video_ids:
        batch.add_request(
            AdVideo(v_id).get_source(fields=['source']),
            success=lambda res, vid=v_id: video_callback(res, vid)
        )

    # 4. 일괄 실행 (Network I/O 최적화)
    if unique_video_ids:
        batch.execute()
    
    return video_url_map


def AnalyzeMetaHeader(campaigns):
    usage_header = campaigns.headers().get('x-business-use-case-usage')
    
    if usage_header:
        usage_data = json.loads(usage_header)
        print("\n" + "="*60)
        print("🚨 [실시간 광고 계정 API 부하 모니터링]")
        # 계정 ID 키를 찾아 내부 데이터 출력
        for act_id, info in usage_data.items():
            metrics = info[0]
            print(f"📍 계정 ID: {act_id}")
            print(f"🔥 CPU 사용량: {metrics.get('total_cputime')}%")
            print(f"📞 호출 횟수: {metrics.get('call_count')}%")
            if metrics.get('estimated_time_to_regain_access') > 0:
                print(f"⏳ 회복 대기 시간: {metrics.get('estimated_time_to_regain_access')}분")
        print("="*60 + "\n")


def Filter_Zero_lp_cost(campaigns, insight_map):
    survivors = []
    for camp in campaigns:
        stat = insight_map.get(camp.get('id'))
        if not stat: continue
        
        costs = stat.get('cost_per_action_type', [])
        lp_cost = float(next((i['value'] for i in costs if i['action_type'] == 'landing_page_view'), 0.0))
        
        if lp_cost >= 0.1: # 성과가 있는 캠페인만 선정
            survivors.append(camp)

    return survivors


def get_Video_IDs_Only_For_Survivors(survivors) -> dict:
    video_id_map = {} # {campaign_id: video_id}

    # 1. 50개씩 끊어서 처리 (C++의 페이징 처리와 동일)
    for i in range(0, len(survivors), 50):
        # 🔥 중요: 루프 안에서 매번 새로운 배치 객체를 생성해야 합니다!
        batch = FacebookAdsApiBatch(FacebookAdsApi.get_default_api())
        chunk = survivors[i:i + 50]
        
        print(f"DEBUG: {i}번째부터 {i+len(chunk)}번째까지 배치 처리 중...")

        def callback(response, camp_id):
            if not response.error():
                ads = response.json().get('data', [])
                if ads:
                    # 첫 번째 광고의 video_id 추출
                    v_id = ads[0].get('creative', {}).get('video_id')
                    if v_id: video_id_map[camp_id] = v_id

        for camp in chunk:
            batch.add_request(
                camp.get_ads(fields=['creative{video_id}'], pending=True),
                success=lambda res, cid=camp.get('id'): callback(res, cid)
            )
        
        # 50개가 찰 때마다 한 번씩 실행
        print("Batch Execute ! ")

    return video_id_map


def get_Video_IDs_Only_For_Survivors_test(survivors, account) -> dict:
    video_id_map = {}
    if not survivors: return video_id_map

    # 1. 살아남은 캠페인 ID들만 추출
    survivor_ids = [s.get('id') for s in survivors]
    
    # 2. 50개씩 끊어서 정밀 조회 (IN 필터 사용)
    for i in range(0, len(survivor_ids), 50):
        chunk_ids = survivor_ids[i:i+50]
        
        # 해당 ID들만 타겟팅해서 'ads'와 'video_id'를 한꺼번에 가져옴
        # 이 방식은 SDK의 필드 경고를 우회하며 가장 확실하게 데이터를 가져옵니다.
        """
        target_campaigns = account.get_campaigns(
            fields=['ads{creative{video_id}}'],
            params={'filtering': [{'field': 'id', 'operator': 'IN', 'value': chunk_ids}]}
        )
        """
        #Test해보기 위해 Creative로 변경
        target_campaigns = account.get_campaigns(
            fields=['ads{creative{id, video_id}}'], # id(Creative ID)를 추가로 가져옴
            params={'filtering': [{'field': 'id', 'operator': 'IN', 'value': chunk_ids}]}
            )
        
        for camp in target_campaigns:

            ads_raw = camp.get('ads')

            if isinstance(ads_raw, dict):
                ads_data = ads_raw.get('data', [])
                print("ads_raw Type Dict")

            elif isinstance(ads_raw, list):
                ads_data = ads_raw

            else:
                ads_data = []
                print("ads_raw Type Error????????")

            if ads_data:
                #Testcode Start
                creative = ads_data[0].get('creative')
                if creative:
                    # 2. [값 저장 변경] 이제 video_id가 아닌 creative의 id를 추출합니다.
                    c_id = creative.get('id') 
                    if c_id:
                        # 캠페인 ID와 크리에이티브 ID를 매핑하여 저장
                        video_id_map[camp.get('id')] = c_id
                #Testcode End

                """ 잠시 보류
                # 첫 번째 광고의 비디오 ID 추출
                v_id = ads_data[0].get('creative', {}).get('video_id')
                if v_id:
                    video_id_map[camp.get('id')] = v_id
                """


    return video_id_map


def get_Video_Urls_Batch_Optimized(video_ids) -> dict:
    """
    전달받은 비디오 ID들에 대해서만 실제 소스 URL을 한 번에 가져옴
    """
    video_url_map = {}
    if not video_ids:
        print("🚨 [CRITICAL] video_ids가 비어있습니다. 이전 단계를 확인하세요!")
        return video_url_map

    batch = FacebookAdsApiBatch(FacebookAdsApi.get_default_api())
    
    # 중복 제거 (여러 광고가 같은 영상을 쓸 수 있으므로)
    unique_ids = list(set(video_ids))
    print(f"🔎 [BATCH START] 총 {len(unique_ids)}개의 고유 비디오 URL 수집 시작")

    # 50개씩 분할 처리하여 안정성 확보
    for i in range(0, len(unique_ids), 50):
        batch = FacebookAdsApiBatch(FacebookAdsApi.get_default_api())
        chunk = unique_ids[i:i+50]
        print(f"📦 [CHUNK] {i} ~ {i+len(chunk)}개 처리 시도 중...")
        
        def success_callback(response, cid):
            print(f"✅ [SUCCESS] ID {cid} 콜백 도달!")
            if not response.error():
                #TestCode Start
                # 💡 [핵심] source 대신 권한 장벽이 낮은 preview_url을 추출합니다.
                # 필요하다면 썸네일 주소인 'image_url'도 함께 가져올 수 있습니다.
                data = response.json()
                # 1순위: 썸네일, 2순위: 이미지 URL 중 있는 것을 가져옵니다.
                final_url = data.get('thumbnail_url') or data.get('image_url')
        
                if final_url:
                    video_url_map[cid] = final_url
                    print(f"✅ [SUCCESS] Creative {cid} 이미지 주소 확보!")
                #TestCode End
                """잠시 보류
                source_url = response.json().get('source', '')
                if source_url: video_url_map[v_id] = source_url
                """

        def failure_callback(response, v_id):
            #TestCode Start
            print(f"❌ [FAILURE] Creative {c_id} 여전히 거부됨")
            print(f"   ㄴ 이유: {response.error().api_error_message()}")
            #TestCode End

            """잠시 보류
            print(f"❌ [FAILURE] ID {v_id} 요청 실패!")
            print(f"   ㄴ 에러 메시지: {response.error().api_error_message()}")
            """
            
            
            """ 잠시 보류
        for v_id in chunk:
            batch.add_request(
                AdVideo(v_id).api_get(fields=['source'], pending=True),
                success=lambda res, vid=v_id: success_callback(res, vid),
                failure=lambda res, vid=v_id: failure_callback(res, vid) # 실패 콜백 추가
            )
            """
            #TestCode Start
        for c_id in chunk:
             batch.add_request(
          # AdVideo가 아닌 AdCreative 객체를 생성하여 접근!
             AdCreative(c_id).api_get(fields=['thumbnail_url', 'image_url', 'name'], pending=True), 
             success=lambda res, cid=c_id: success_callback(res, cid),
             failure=lambda res, vid=c_id: failure_callback(res, vid)
                )
             #TestCode End
        try:
            print(f"🚀 [EXECUTE] {len(chunk)}개 배치 전송!")
            batch.execute()
            print("🏁 [FINISH] 해당 청크 배치 실행 완료")
        except Exception as e:
            print(f"🔥 [FATAL] 배치 실행 중 예외 발생: {e}")


    return video_url_map