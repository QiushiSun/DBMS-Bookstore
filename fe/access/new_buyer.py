from fe import conf
from fe.access import buyer, auth


def register_new_buyer(user_id, password) -> buyer.Buyer:
    a = auth.Auth(conf.URL)
    code = a.register(user_id, password)
    assert code == 200
    s = buyer.Buyer(conf.URL, user_id, password)
    return s

def register_new_buyer_auth(user_id, password) -> (buyer.Buyer,auth.Auth):
    a = auth.Auth(conf.URL)
    code = a.register(user_id, password)
    assert code == 200
    s = buyer.Buyer(conf.URL, user_id, password)
    return s,a