import flet as ft
import asyncio
import Facebook_Campaign_fetcher
import ConfigReader

class AppController:
    def __init__(self, view):
        self.view = view  # UI 컴포넌트들이 담긴 객체

    async def handle_fetch_data(self, event):
        page = event.page
        self.view.pr.visible = True
        self.view.status_text.value = "데이터 수집 중..."
        page.update()

        try:
            auth = ConfigReader.ReadConfigFile("Config.config")
            await asyncio.sleep(0.1)

            Facebook_Campaign_fetcher.do_Facebook_Init(auth.APP_ID, auth.APP_SECRET, auth.ACCESS_TOKEN)
            retval = Facebook_Campaign_fetcher.fetch_campaign_stats_objects(auth.AD_ACCOUNT_ID)

            stats = sorted(retval, key=lambda x: x.lp_cost, reverse=True)

            # UI 업데이트 호출
            self.view.update_table(stats)
            self.view.status_text.value = f"{len(stats)}개 로드 완료"
            self.view.status_text.color = 'green'

        except Exception as ex:
            self.view.status_text.value = f"에러: {str(ex)}"
            self.view.status_text.color = 'red'

        self.view.pr.visible = False
        page.update()