import requests
from typing import Any, TypedDict


class TradingModes(TypedDict):
    shares: list[str]
    bonds: list[str]


BASE_URL = 'https://iss.moex.com/iss/engines/stock/markets'
TRADING_MODES: TradingModes = {
    'shares': ['TQBR', 'TQTF'],
    'bonds': ['TQCB', 'TQOB', 'TQIR']
}


class MoexClient:
    """Клиент для получения данных с MOEX API"""

    def __init__(self):
        self.session = requests.Session()
        self._cache: dict[str, Any] = {}

    def _get_data(self, url: str, section: str) -> list[list]:
        """Получает данные с MOEX с кэшированием"""

        if url in self._cache:
            return self._cache[url]

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка запроса к MOEX: {url}\n{e}")

        data = response.json()[section]['data']
        self._cache[url] = data
        return data

    def get_last_prices(self, tickers: list[str], bond_tickers: list[str]) -> dict[str, float | None]:
        """Получает последние цены для акций и облигаций"""

        prices: dict[str, float | None] = {}

        for market, boards in TRADING_MODES.items():
            for board in boards:
                url = (f"{BASE_URL}/{market}/boards/{board}/securities.json"
                       f"?iss.meta=off&iss.only=marketdata&marketdata.columns=SECID,LAST")
                data = self._get_data(url, 'marketdata')

                for row in data:
                    ticker, last_price = row[0], row[1]
                    if ticker in tickers or ticker in bond_tickers:
                        if ticker in bond_tickers and last_price:
                            prices[ticker] = round(last_price * 10, 2)
                        else:
                            prices[ticker] = last_price

        return prices

    def get_coupon_data(self, tickers: list[str]) -> dict[str, float]:
        """Получает НКД облигаций"""

        coupons: dict[str, float] = {}

        for board in TRADING_MODES['bonds']:
            url = (f"{BASE_URL}/bonds/boards/{board}/securities.json"
                   f"?iss.meta=off&iss.only=securities&securities.columns=SECID,ACCRUEDINT")
            data = self._get_data(url, 'securities')

            for row in data:
                ticker, accrued_int = row[0], row[1]
                if ticker in tickers:
                    coupons[ticker] = accrued_int

        return coupons
