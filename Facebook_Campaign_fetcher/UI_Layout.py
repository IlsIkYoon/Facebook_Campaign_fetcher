import flet as ft

class AppView:
    def __init__(self, page: ft.Page):
        self.page = page

        # 멤버 변수로 UI 요소들을 들고 있음 (C++ 클래스 멤버와 동일)
        self.config_input = ft.TextField(label="Config Path", value="Config.config")
        self.status_text = ft.Text("준비됨")
        self.pr = ft.ProgressBar(visible=False)

        self.stats_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("캠페인명")),
                ft.DataColumn(ft.Text("랜딩페이지 비용"), numeric=True),
                ft.DataColumn(ft.Text("구매 전환"), numeric=True),
                ft.DataColumn(ft.Text("ROAS"), numeric=True),
                ft.DataColumn(ft.Text("CTR"), numeric=True),
                ft.DataColumn(ft.Text("지출비율"), numeric=True), 
            ],
            rows=[],
            # 컬럼 간 간격 조정 (C++의 ColumnWidth 조정과 유사)
            column_spacing=20, 
        )

    def build(self, controller):
        # 레이아웃 배치 및 컨트롤러 연결
        return ft.Column(
        controls=[
            ft.Text("📊 Meta Ads Performance Dashboard", size=25, weight="bold"),
            self.status_text,
            self.pr,
            ft.ElevatedButton("수집 시작", on_click=controller.handle_fetch_data),

            
            # 세로/가로 스크롤이 모두 가능하도록 구성
            ft.Column(
                [
                    ft.Row([self.stats_table], scroll=ft.ScrollMode.ALWAYS) # 가로 스크롤
                ],
                scroll=ft.ScrollMode.ALWAYS, # 세로 스크롤
                expand=True
            )
        ], expand=True)

    def update_table(self, stats_list):
        self.stats_table.rows.clear()
        for s in stats_list:
            # 2. 데이터 포맷팅 (C++의 sprintf나 format과 비슷합니다)
            self.stats_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(s.name)),                                  # 캠페인명
                    ft.DataCell(ft.Text(f"{int(s.lp_cost):,}원")),                 # LP 비용
                    ft.DataCell(ft.Text(f"{int(s.conv)}건")),                      # 구매 전환
                    ft.DataCell(ft.Text(f"{s.roas:.2f}")),                         # ROAS
                    ft.DataCell(ft.Text(f"{getattr(s, 'ctr', 0):.2f}%")),          # CTR
                    ft.DataCell(ft.Text(f"{getattr(s, 'spend_ratio', 0):.1f}%")),  # 지출비율
                ])
            )