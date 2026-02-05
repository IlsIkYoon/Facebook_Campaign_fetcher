import Facebook_Campaign_fetcher
import Table_Print
import ExcelMaker
import ConfigReader


def main():
    authData = ConfigReader.ReadConfigFile('Config.config')

    Facebook_Campaign_fetcher.do_Facebook_Init(authData.APP_ID, authData.APP_SECRET, authData.ACCESS_TOKEN)

    stats_list = Facebook_Campaign_fetcher.fetch_campaign_stats_objects(authData.AD_ACCOUNT_ID)

    # ROAS 기준 내림차순 정렬
    sorted_by_lp_cost = sorted(stats_list, key=lambda x: x.lp_cost, reverse=True)
    # 지출 비율(spend_ratio) 기준 오름차순 정렬
    sorted_by_budget = sorted(stats_list, key=lambda x: x.conv, reverse = True)
    Table_Print.print_stats_table(sorted_by_lp_cost)
    Table_Print.print_stats_table(sorted_by_budget)
    
    ExcelMaker.export_stats_to_excel(sorted_by_lp_cost, "ExcelTest.xlsx")



if __name__ == "__main__":
    main()
