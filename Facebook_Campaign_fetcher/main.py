import Facebook_Campaign_fetcher
import Table_Print


ACCESS_TOKEN = 'EAAMy3As4sIgBQsLwGRotFO9m1367cHTOKPc6WpqG2QfZAcDPNBWnBzEZBFoDC70wMdlh8m7kAKcYqi9viiovwCnpkUw8tWCQowGJZCeDZBSyF6SCNrzEPZCmJ2QoVtGnBjUElIWGyWuwjMjnLh14m0W1nx88lBtjYSqKRsVBz4VpUBSdG2ZAVqsZAX8rAsG0ucTS1ysJDq8'
AD_ACCOUNT_ID = 'act_609787644136633'
APP_ID = '900345592590472'
APP_SECRET = '2e296dff64c5e4341b24b3a7dad46d3b'

def main():
    Facebook_Campaign_fetcher.do_Facebook_Init(APP_ID, APP_SECRET, ACCESS_TOKEN)
    #Facebook_Campaign_fetcher.get_my_campaigns(AD_ACCOUNT_ID)
    #Facebook_Campaign_fetcher.get_my_campaigns_with_costs(AD_ACCOUNT_ID)
    #Facebook_Campaign_fetcher.get_marketing_metrics(AD_ACCOUNT_ID)
    #Facebook_Campaign_fetcher.get_filtered_metrics(AD_ACCOUNT_ID)
    stats_list = Facebook_Campaign_fetcher.fetch_campaign_stats_objects(AD_ACCOUNT_ID)
    # ROAS 기준 내림차순 정렬
    sorted_by_lp_cost = sorted(stats_list, key=lambda x: x.lp_cost, reverse=True)
    # 지출 비율(spend_ratio) 기준 오름차순 정렬
    sorted_by_budget = sorted(stats_list, key=lambda x: x.spend_ratio)
    Table_Print.print_stats_table(sorted_by_lp_cost)







if __name__ == "__main__":
    main()
