from typing import Any

from app.retail_network.base import RetailPaymentNetwork
from app.retail_network.easy_pay_network import EasyPayNetwork
from app.retail_network.generic_voucher_network import GenericVoucherNetwork
from app.retail_network.pay_at_network import PayAtNetwork

_NETWORKS: dict[str, type] = {
    "pay_at": PayAtNetwork,
    "easy_pay": EasyPayNetwork,
    "kazang": lambda config=None: GenericVoucherNetwork("kazang", "Kazang", ["kazang_agents", "retail"], config),
    "flash": lambda config=None: GenericVoucherNetwork("flash", "Flash", ["flash_agents"], config),
    "shoprite": lambda config=None: GenericVoucherNetwork("shoprite", "Shoprite", ["shoprite", "checkers"], config),
    "pick_n_pay": lambda config=None: GenericVoucherNetwork("pick_n_pay", "Pick n Pay", ["pick_n_pay", "boxer"], config),
}


def get_retail_network(network_code: str, config: dict[str, Any] | None = None) -> RetailPaymentNetwork:
    factory = _NETWORKS.get(network_code)
    if not factory:
        raise ValueError(f"Unknown retail payment network: {network_code}")
    if network_code in ("pay_at", "easy_pay"):
        return factory(config)
    return factory(config)


def list_retail_networks() -> list[str]:
    return list(_NETWORKS.keys())
