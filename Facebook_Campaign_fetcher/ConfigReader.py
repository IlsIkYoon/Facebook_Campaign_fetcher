import os
import AppData

class ConfigLoader:
    def __init__(self, file_path="Config.config"):
        self.configs = {}
        self.load(file_path)

    def load(self, file_path):
        if not os.path.exists(file_path):
            print(f"경고: {file_path} 파일을 찾을 수 없습니다.")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 빈 줄이거나 주석(#)인 경우 건너뜀
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    # '='를 기준으로 key와 value 분리 (최대 1번만 분리)
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # 따옴표 제거 처리 ("값" 또는 '값' 형태)
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    self.configs[key] = value

    def get(self, key, default=None):
        """C++의 map.find()와 유사하게 안전하게 값을 가져옴"""
        return self.configs.get(key, default)

    def __getattr__(self, item):
        """config.key 형태로 접근할 수 있게 해주는 파이썬의 마법 메서드"""
        return self.configs.get(item)




def ReadConfigFile(file_path = "Config.config"):
    config = ConfigLoader('Config.config')
    
    auth_data = AppData.AppAuthData()
    auth_data.APP_ID = config.get('APP_ID')
    auth_data.APP_SECRET = config.get('APP_SECRET')
    auth_data.ACCESS_TOKEN = config.get('ACCESS_TOKEN')
    auth_data.AD_ACCOUNT_ID = config.get('AD_ACCOUNT_ID')

    return auth_data

