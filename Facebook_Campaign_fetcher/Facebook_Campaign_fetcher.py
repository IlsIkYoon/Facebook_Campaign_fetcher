from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign

# 인증 정보 (본인의 정보로 교체하세요)
ACCESS_TOKEN = 'EAANPkY8RYDABQnVxCpZAqurHFobYUUsgSOEgXVbL1U4SaCsMpclOJOXWOTYM1CDwP7TWzAxQCjhYmiR0yabIMd7qJbZAneZBytAZCSQfFwzn3nOVMJCVYZCMBNodD3r3pBV6WTQbGlumXrT84hoxeBLb2cCr7DOTOHUNMeovlMhjINpTceZASanq3HcxhlsNSdzgZDZD'
AD_ACCOUNT_ID = 'act_YOUR_AD_ACCOUNT_ID'
APP_ID = 'YOUR_APP_ID'
APP_SECRET = 'YOUR_APP_SECRET'

# API 초기화
FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)

def get_my_campaigns():
    # 광고 계정 객체 생성
    account = AdAccount(AD_ACCOUNT_ID)
    
    # [중요] 가져올 필드 목록 정의
    # C++의 Structure 멤버를 선택한다고 생각하시면 됩니다.
    fields = [
        Campaign.Field.id,
        Campaign.Field.name,
        Campaign.Field.status,
        Campaign.Field.objective,
        Campaign.Field.daily_budget,
        Campaign.Field.start_time,
    ]
    
    # 캠페인 데이터 요청 (Paging이 자동으로 처리되는 Iterator를 반환합니다)
    campaigns = account.get_campaigns(fields=fields)
    
    print(f"{'ID':<20} | {'Name':<30} | {'Status':<10} | {'Budget':<10}")
    print("-" * 80)
    
    for campaign in campaigns:
        # 데이터가 없는 경우(예: 예산 미설정 등)를 대비해 get() 사용
        name = campaign.get(Campaign.Field.name, 'N/A')
        c_id = campaign.get(Campaign.Field.id, 'N/A')
        status = campaign.get(Campaign.Field.status, 'N/A')
        
        # 예산은 'cents' 단위로 올 수 있으므로 주의가 필요합니다.
        budget = campaign.get(Campaign.Field.daily_budget, '0')
        
        print(f"{c_id:<20} | {name[:28]:<30} | {status:<10} | {budget:<10}")

if __name__ == "__main__":
    get_my_campaigns()