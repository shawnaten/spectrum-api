from django.test import TestCase
from cal.tasks import sync


class TestSync(TestCase):
    def test_sync(self):
        name = "Spectrum General"
        cal_id = ("spectrumatutsa.org_o4gn1t9sl0e5cd3hr4451v3rig"
                  "@group.calendar.google.com")
        result = sync.delay(name, cal_id)
        print(result.get(timeout=5))

#    @classmethod
#    def setUpTestData(cls):
#        # Set up data for the whole TestCase
