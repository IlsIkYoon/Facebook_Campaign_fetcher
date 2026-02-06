import flet as ft
import flet_video  as ftv
import webbrowser


class AppView:
    def __init__(self, page: ft.Page):
        self.page = page

        # 비디오 플레이어 초기화 (C++의 미디어 객체 선언)
        
        self.video_player = ftv.Video(
            expand=True,
            playlist=[], 
            playlist_mode=ftv.PlaylistMode.LOOP,
            fill_color="black",
            aspect_ratio=16/9,
            autoplay=False, # 대시보드이므로 클릭 시에만 재생되게 설정
        )

       # 2. 비디오를 띄울 다이얼로그 (팝업창)
        self.video_dialog = ft.AlertDialog(
            title=ft.Text("소재 미리보기", weight="bold"),
            content=ft.Container(
                content=self.stats_video_container(), # 비디오를 담은 컨테이너
                width=800, 
                height=500
            ),
            actions=[
                ft.TextButton("닫기", on_click=lambda _: self.close_video())
            ],
        )



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
                ft.DataColumn(ft.Text("미리보기")),
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
            # 1. URL 존재 여부 확인 (버튼 활성화 여부 결정)
            url = getattr(s, 'video_url', None)
            has_video = True if url else False

            # 2. 데이터 포맷팅 (C++의 sprintf나 format과 비슷합니다)
            self.stats_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(s.name)),                                  # 캠페인명
                    ft.DataCell(ft.Text(f"{int(s.lp_cost):,}원")),                 # LP 비용
                    ft.DataCell(ft.Text(f"{int(s.conv)}건")),                      # 구매 전환
                    ft.DataCell(ft.Text(f"{s.roas:.2f}")),                         # ROAS
                    ft.DataCell(ft.Text(f"{getattr(s, 'ctr', 0):.2f}%")),          # CTR
                    ft.DataCell(ft.Text(f"{getattr(s, 'spend_ratio', 0):.1f}%")),  # 지출비율

                    ft.DataCell(
                    
                    #ft.TextButton(content=ft.Text("재생"), on_click=lambda e, url=s.video_url: self.open_video(url)),
                     
                    ft.IconButton(
                    icon= ft.Icons.PLAY_CIRCLE_FILL_OUTLINED if has_video else ft.Icons.PLAY_DISABLED,  # 1. 'icon=' 키워드가 명확히 있어야 함
                    icon_color="blue" if has_video else "grey",          # 2. 색상 지정
                    tooltip="소재 보기(브라우저 실행)" if has_video else "소재 없음",         # 3. 마우스 올렸을 때 설명 (C++의 Tooltip)
                    on_click=lambda e, video_url=url: self.open_video(video_url)
                    )
                    
                ),
                ])
            )

    def stats_video_container(self):
        # 비디오 플레이어를 감싸는 세련된 컨테이너 (C++의 Wrapper Class 느낌)
        return ft.Column([
            self.video_player,
            ft.Text("※ Meta API에서 제공하는 임시 프리뷰 영상입니다.", size=12, color="grey")
        ])

    def open_video(self, video_url):
        if not video_url: return

        clean_url = str(video_url).strip()
        print(f"🚀 브라우저 호출 시도: {clean_url}")

        try:
            webbrowser.open(clean_url)
            
        except Exception as e:
            print(f"❌ [ERROR] 브라우저 호출 실패: {e}")

    def close_video(self):
        self.video_dialog.open = False
        self.video_player.pause() # 리소스 점유 해제 (중요!)
        self.page.update()

