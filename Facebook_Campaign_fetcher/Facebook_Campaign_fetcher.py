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

def get_filtered_stats(campaigns, all_insights, insight_map) -> List[CampaignStats]:
    results: List[CampaignStats] = []

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


def fetch_campaign_stats_objects(accountID: str) -> List[CampaignStats]:
    """
    메타 데이터를 수집하여 CampaignStats 객체 리스트를 반환
    """
    account = AdAccount(accountID)

    campaigns = get_All_Campaigns(account)
    all_insights = get_All_Insight(account)
    
    insight_map = {item['campaign_id']: item for item in all_insights}

    return get_filtered_stats(campaigns, all_insights, insight_map)