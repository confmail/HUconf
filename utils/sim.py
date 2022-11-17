from time import sleep

import requests

from utils import gsheets


class Sim:
    def __init__(self, country, product, max_price=10):
        self.s = requests.Session()
        self.api_key = gsheets.get_data('config', 'sim_key')
        self.sim_id, self.sim_phone = self.get_new_number(country, product, max_price)

    def get_new_number(self, country, product, max_price = 10):
        for _ in range(6):
            try:
                r = self.s.get(f'https://5sim.net/v1/guest/prices?country={country}&product={product}')
                if r.status_code == 200:
                    prices = r.json()[country][product]
                else:
                    raise RuntimeError(f'Ошибка 5sim({r.status_code}): {r.text}')
                valid_operators = {k: v for k, v in prices.items() if v['count'] and v['cost'] < max_price}
                operator = list(valid_operators.keys())[0]

                headers = {'Authorization': f"Bearer {self.api_key}", 'Accept': 'application/json', }
                r = self.s.get(f'https://5sim.net/v1/user/buy/activation/{country}/{operator}/{product}',
                               headers=headers)
                break
            except Exception:
                pass
        else:
            raise RuntimeError('Не могу получить номер')
        return r.json()['id'], r.json()['phone']

    def get_new_code(self, latest_code=None):
        code = None
        for _ in range(6):
            try:
                headers = {'Authorization': f"Bearer {self.api_key}", 'Accept': 'application/json', }
                r = self.s.get(f'https://5sim.net/v1/user/check/{self.sim_id}', headers=headers)
                if r.json()['sms']:
                    new_code = r.json()['sms'][-1]['code']
                else:
                    new_code = None
                if new_code != latest_code:
                    code = new_code
                    break
            except Exception:
                pass
            sleep(10)
        return code

    def ban_sim(self):
        headers = {'Authorization': f"Bearer {self.api_key}", 'Accept': 'application/json', }
        self.s.get(f'https://5sim.net/v1/user/ban/{self.sim_id}', headers=headers)
