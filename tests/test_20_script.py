import json

from fedoidcmsg import MetadataStatement
from fedoidcmsg.bundle import jwks_to_keyjar
from fedoidcmsg.utils import request_signed_by_signing_keys
from fedoidcmsg.utils import self_sign_jwks
from fedoidcmsg.utils import verify_request_signed_by_signing_keys
from fedoidcmsg.utils import verify_self_signed_jwks

from oidcmsg.key_jar import KeyJar
from oidcmsg.key_jar import build_keyjar

KEYDEFS = [
    {"type": "RSA", "use": ["sig"]},
    {"type": "RSA", "use": ["sig"]},
    {"type": "EC", "crv": "P-256", "use": ["sig"]}
]

JWKS, KEYJAR, _ = build_keyjar(KEYDEFS)


def test_jwks_to_keyjar():
    _kj = jwks_to_keyjar(JWKS)
    assert list(_kj.owners()) == ['']
    assert len(_kj.get_signing_key('RSA',owner='')) == 2
    assert len(_kj.get_signing_key('EC',owner='')) == 1


def test_self_signed_jwks():
    kj = KeyJar()
    kj.issuer_keys['abc'] = KEYJAR.issuer_keys['']
    ssj = self_sign_jwks(kj, 'abc', kid='', lifetime=3600)
    assert ssj

    res = verify_self_signed_jwks(ssj)
    _kj = jwks_to_keyjar(res['jwks'], res['iss'])
    assert list(_kj.owners()) == ['abc']
    assert len(_kj.get_signing_key('RSA',owner='abc')) == 2
    assert len(_kj.get_signing_key('EC',owner='abc')) == 1


def test_request_signed_by_signing_keys():
    kj = KeyJar()
    kj.issuer_keys['abc'] = KEYJAR.issuer_keys['']
    msreq = MetadataStatement(signing_keys=json.dumps(JWKS))
    smsreq = request_signed_by_signing_keys(kj, msreq, 'abc', 3600)

    assert smsreq

    res = verify_request_signed_by_signing_keys(smsreq)

    assert set(res.keys()) == {'ms', 'iss'}
    assert res['iss'] == 'abc'
