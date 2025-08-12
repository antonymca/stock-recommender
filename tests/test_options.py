from signals.options import pick_strategies
from signals.config import Config


def test_bull_call_math():
    cfg = Config()
    strat = pick_strategies(px=100, iv_rank=10, holding_shares=0, cfg=cfg)[0]
    assert strat["name"] == "Bull Call Debit Spread"
    width = cfg.bull_call_width
    est = strat["estimates"]
    assert est["net_debit"] == round(width * 0.25, 2)
    assert est["max_profit"] == round(width - est["net_debit"], 2)
    assert est["breakeven"] == round(strat["legs"][0]["strike"] + est["net_debit"], 2)


def test_bull_put_math():
    cfg = Config()
    strat = pick_strategies(px=100, iv_rank=40, holding_shares=0, cfg=cfg)[0]
    assert strat["name"] == "Bull Put Credit Spread"
    width = cfg.bull_put_width
    est = strat["estimates"]
    assert est["net_credit"] == round(width * 0.3, 2)
    assert est["max_loss"] == round(width - est["net_credit"], 2)


def test_csp_basis():
    cfg = Config()
    strategies = pick_strategies(px=100, iv_rank=40, holding_shares=0, cfg=cfg)
    csp = [s for s in strategies if s["name"] == "Cash-Secured Put"][0]
    strike = csp["legs"][0]["strike"]
    est = csp["estimates"]
    assert est["assigned_basis"] == round(strike - est["credit"], 2)
