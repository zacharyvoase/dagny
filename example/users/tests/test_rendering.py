from django.test import TestCase


def assert_content_type(response, expected):
    actual = response['content-type'].split(';', 1)[0]
    assert actual == expected, \
            "Expected a Content-Type of %r, got %r" % (expected, actual)

class SkipTest(TestCase):

    def test_quality(self):
        # Even though XML has a much higher quality score than JSON, because it
        # raises Skip it should never be processed.
        response = self.client.get("/users/",
                                   HTTP_ACCEPT=("application/xml;q=1,"
                                                "application/json;q=0.1"))

        self.assertEqual(response.status_code, 200)
        assert_content_type(response, 'application/json')

    def test_html_fallback(self):
        # Because XML raises skip, even when it is the only acceptable response
        # type it should still cause the HTML fallback to be used.
        response = self.client.get("/users/", HTTP_ACCEPT="application/xml")

        self.assertEqual(response.status_code, 200)
        assert_content_type(response, 'text/html')


class HTMLFallbackTest(TestCase):

    def test_undefined(self):
        # Asking for an undefined type should trigger the HTML fallback.
        response = self.client.get("/users/", HTTP_ACCEPT="image/png")

        self.assertEqual(response.status_code, 200)
        assert_content_type(response, 'text/html')

    def test_undefined_with_quality(self):
        # Asking for an undefined type with a higher quality than HTML should
        # produce an HTML response.
        response = self.client.get("/users/",
                                   HTTP_ACCEPT=("image/png;q=1.0,"
                                                "text/html;q=0.1"))

        self.assertEqual(response.status_code, 200)
        assert_content_type(response, 'text/html')
