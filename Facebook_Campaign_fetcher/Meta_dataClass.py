from dataclasses import dataclass


@dataclass
class CampaignStats:
    name: str
    conv: int
    ctr: float
    roas: float
    lp_cost: float
    spend_ratio: float
    video_url: str = ""