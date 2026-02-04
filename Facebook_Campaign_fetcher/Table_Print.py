from typing import List
from Meta_dataClass import CampaignStats

def print_stats_table(stats_list: List[CampaignStats]):
    if not stats_list:
        print("Can't find Data...")
        return

    # 헤더 정의 및 구분선
    # 한글 이름을 고려하여 Name 컬럼의 폭을 넉넉히 잡았습니다.
    header = f"{'Campaign Name':<32} | {'Conv':<6} | {'CTR':<7} | {'ROAS':<6} | {'LP Cost':<10} | {'Spend%':<8}"
    separator = "-" * len(header)

    print("\n" + separator)
    print(header)
    print(separator)

    for stat in stats_list:
        # 각 필드 정렬 및 소수점 자리수 제어
        # :<32 (왼쪽 정렬, 32칸), :>6 (오른쪽 정렬, 6칸)
        name_str = stat.name[:30] # 이름이 너무 길면 자름
        
        print(
            f"{name_str:<32} | "
            f"{stat.conv:>6} | "
            f"{stat.ctr:>6.2f}% | "
            f"{stat.roas:>6.2f} | "
            f"{stat.lp_cost:>10,.0f} | "
            f"{stat.spend_ratio:>7.1f}%"
        )
    
    print(separator + "\n")

# --- 사용 예시 ---
# sorted_by_lp_cost = sorted(stats_list, key=lambda x: x.lp_cost, reverse=True)
# print_stats_table(sorted_by_lp_cost)