from __future__ import absolute_import, division, print_function

import pretend
import pytest

from symantecssl.auth import SymantecAuth
from symantecssl.core import Symantec
from symantecssl.session import SymantecSession


@pytest.fixture
def api():
    return Symantec("user", "p@ssw0rd")


class TestSymantec:

    def test_basic_init(self):
        api = Symantec("user", "p@ssw0rd")
        assert api.url == "https://api.geotrust.com/webtrust/partner"
        assert isinstance(api.session, SymantecSession)
        assert isinstance(api.session.auth, SymantecAuth)
        assert api.session.auth.username == "user"
        assert api.session.auth.password == "p@ssw0rd"

    def test_init_with_url(self):
        api = Symantec("user", "p@ssw0rd", url="https://api.example.com/")
        assert api.url == "https://api.example.com/"

    def test_submit(self, api):
        resp = pretend.stub(
            content=pretend.stub(),
            raise_for_status=pretend.call_recorder(lambda: None),
        )
        api.session = pretend.stub(
            post=pretend.call_recorder(lambda *a, **k: resp),
        )

        serialized = pretend.stub()
        results = pretend.stub()
        obj = pretend.stub(
            serialize=pretend.call_recorder(lambda: serialized),
            response=pretend.call_recorder(lambda data: results),
        )

        assert api.submit(obj) is results
        assert api.session.post.calls == [
            pretend.call(
                "https://api.geotrust.com/webtrust/partner",
                serialized,
            ),
        ]
        assert resp.raise_for_status.calls == [pretend.call()]
        assert obj.serialize.calls == [pretend.call()]
        assert obj.response.calls == [pretend.call(resp.content)]

    def test_order(self, api):
        order_instance = pretend.stub()
        results = pretend.stub()
        api.order_class = pretend.call_recorder(lambda **kw: order_instance)
        api.submit = pretend.call_recorder(lambda o: results)

        assert api.order(foo="bar") is results
        assert api.order_class.calls == [pretend.call(foo="bar")]
        assert api.submit.calls == [pretend.call(order_instance)]
