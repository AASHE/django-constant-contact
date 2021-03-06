import time
import uuid
import unittest

from django.conf import settings
import django.test

from .models import (ConstantContact,
                     ConstantContactAPIError,
                     EmailMarketingCampaign)


ORG_ADDRESS = {
    'organization_name': 'My Organization',
    'address_line_1': '123 Maple Street',
    'address_line_2': 'Suite 1',
    'address_line_3': '',
    'city': 'Anytown',
    'state': 'MA',
    'international_state': '',
    'postal_code': '01444',
    'country': 'US'
}


# Define assertIn here, since it doesn't live on unittest.TestCase
# until Python 2.7.
def assertIn(self, test_value, expected_set):
    msg = "%s did not occur in %s" % (test_value, expected_set)
    self.assert_(test_value in expected_set, msg)


class ConstantContactTests(unittest.TestCase):

    def setUp(self):
        self.cc = ConstantContact()
        self.email_marketing_campaign = None
        self.email_marketing_campaign_kwargs = {
            'name': 'Test Campaign {0}'.format(uuid.uuid4()),
            'email_content': '<html><body>Test Email Content</body></html>',
            'from_email': settings.CONSTANT_CONTACT_FROM_EMAIL,
            'from_name': 'Test Sender',
            'reply_to_email': settings.CONSTANT_CONTACT_REPLY_TO_EMAIL,
            'subject': 'Test Subject',
            'text_content': '<text>Test Text Content</text>',
            'address': ORG_ADDRESS}
        time.sleep(1)  # So we don't run over our queries-per-second quota.

    def tearDown(self):
        if self.email_marketing_campaign:
            # Call delete on any email marketing campaign
            # we created, which should also delete it up
            # on Constant Contact's servers.
            self.email_marketing_campaign.delete()

    def test_connect(self):
        response = self.cc.api.get('/account/info')
        self.assertEqual(200, response.status_code)

    def test_create_email_marketing_campaign(self):
        self.email_marketing_campaign = self.cc.new_email_marketing_campaign(
            **self.email_marketing_campaign_kwargs)
        assert isinstance(self.email_marketing_campaign,
                          EmailMarketingCampaign)

    def test_update_email_marketing_campaign(self):
        """Can we update an Email Marketing Campaign?
        Will fail if test_create_email_marketing_campaign fails.
        """
        self.email_marketing_campaign = self.cc.new_email_marketing_campaign(
            **self.email_marketing_campaign_kwargs)

        update_kwargs = self.email_marketing_campaign_kwargs
        updated_subject = (
            self.email_marketing_campaign.data['subject'] + 'Tom Brady')
        update_kwargs['subject'] = updated_subject
        update_kwargs['email_marketing_campaign'] = (
            self.email_marketing_campaign)

        self.email_marketing_campaign = (
            self.cc.update_email_marketing_campaign(**update_kwargs))

        self.assertEqual(updated_subject,
                         self.email_marketing_campaign.data['subject'])

    def test_delete_email_marketing_campaign(self):
        """Can we delete an email marketing campaign?
        """
        email_marketing_campaign = self.cc.new_email_marketing_campaign(
            **self.email_marketing_campaign_kwargs)
        self.cc.delete_email_marketing_campaign(
            email_marketing_campaign)

    def test_failed_delete_email_marketing_campaign_raises_exception(self):
        """When a delete fails, is an exception raised?
        """
        # Try to delete a bogus ID:
        email_marketing_campaign = EmailMarketingCampaign.objects.create(
            data={'id': 1})
        self.assertRaises(ConstantContactAPIError,
                          self.cc.delete_email_marketing_campaign,
                          email_marketing_campaign)

    def test_server_version_is_removed_upon_delete_of_email_marketing_campaign(
            self):
        """When EmailMarketingCampaign deleted, is the CC version deleted?
        """
        email_marketing_campaign = self.cc.new_email_marketing_campaign(
            **self.email_marketing_campaign_kwargs)
        # GET the email marketing campaign:
        cc = ConstantContact()
        url = cc.api.join('/'.join([
            cc.EMAIL_MARKETING_CAMPAIGN_URL,
            str(email_marketing_campaign.data['id'])]))
        response = url.get()
        self.assertEqual(200, response.status_code)
        # Delete the EmailMarketingCampaign:
        email_marketing_campaign.delete()
        # Same GET should 404 now:
        response = url.get()
        self.assertEqual(404, response.status_code)

    def test_inline_css(self):
        """Can we inline CSS?
        """
        html = """
        <html>
          <head>
            <style type="text/css">
             body {
               width: 100%;
             }
             a {
               text-decoration: none;
             }
             .section {
               padding-top: 5px;
             }
            </style>
          </head>
          <body>
            <div class="section">
              <a href="#"></a>
            </div>
          </body>
        </html>
        """
        expected_inlined_html = """
        <html>
          <head>
          </head>
          <body style="width: 100%">
            <div class="section" style="padding-top: 5px">
              <a href="#" style="text-decoration: none"></a>
            </div>
          </body>
        </html>
        """
        inlined_html = self.cc.inline_css(html)
        whitespaceless_expected_inlined_html = (
            ''.join(expected_inlined_html.split(expected_inlined_html)))
        whitespaceless_inlined_html = ''.join(inlined_html.split(inlined_html))

        self.assertEqual(whitespaceless_expected_inlined_html,
                         whitespaceless_inlined_html)

    def test_preview_email_marketing_campaign(self):
        """Can we preview an Email Marketing Campaign?

        Pretty weak test.  Makes no assertions.
        """
        self.email_marketing_campaign = self.cc.new_email_marketing_campaign(
            **self.email_marketing_campaign_kwargs)
        html, text = self.cc.preview_email_marketing_campaign(
            self.email_marketing_campaign)

    def test_create_view_as_webpage(self):
        """Can we set the "view as webpage" flag when we create an EMC?
        """
        link_text = 'bzxbnxzcvxczvnbmxcvzxcvcvxnbv'
        page_text = 'uioqweriuoerwiueriuerwuiweriu'

        kwargs = self.email_marketing_campaign_kwargs
        kwargs['is_view_as_webpage_enabled'] = True
        kwargs['view_as_web_page_link_text'] = link_text
        kwargs['view_as_web_page_text'] = page_text
        self.email_marketing_campaign = self.cc.new_email_marketing_campaign(
            **kwargs)
        html, text = self.cc.preview_email_marketing_campaign(
            self.email_marketing_campaign)
        assertIn(self, link_text, html)
        assertIn(self, page_text, html)

    def test_update_view_as_webpage(self):
        """Can we set the "view as webpage" flag when we update an EMC?
        """
        self.email_marketing_campaign = self.cc.new_email_marketing_campaign(
            **self.email_marketing_campaign_kwargs)

        link_text = 'bzxbnxzcvxczvnbmxcvzxcvcvxnbv'
        page_text = 'uioqweriuoerwiueriuerwuiweriu'

        kwargs = self.email_marketing_campaign_kwargs
        kwargs['email_marketing_campaign'] = self.email_marketing_campaign
        kwargs['is_view_as_webpage_enabled'] = True
        kwargs['view_as_web_page_link_text'] = link_text
        kwargs['view_as_web_page_text'] = page_text
        self.email_marketing_campaign = (
            self.cc.update_email_marketing_campaign(**kwargs))
        html, text = self.cc.preview_email_marketing_campaign(
            self.email_marketing_campaign)
        assertIn(self, link_text, html)
        assertIn(self, page_text, html)

    def test_create_set_permission_reminder(self):
        """Can we set the permission reminder flag when we create an EMC?
        """
        reminder_text = '45646564788794561232456786453'

        kwargs = self.email_marketing_campaign_kwargs
        kwargs['is_permission_reminder_enabled'] = True
        kwargs['permission_reminder_text'] = reminder_text
        self.email_marketing_campaign = self.cc.new_email_marketing_campaign(
            **kwargs)
        html, text = self.cc.preview_email_marketing_campaign(
            self.email_marketing_campaign)
        assertIn(self, reminder_text, html)

    def test_update_set_permission_reminder(self):
        """Can we set the permission reminder flag when we update an EMC?
        """
        self.email_marketing_campaign = self.cc.new_email_marketing_campaign(
            **self.email_marketing_campaign_kwargs)

        reminder_text = '45646564788794561232456786453'

        kwargs = self.email_marketing_campaign_kwargs
        kwargs['email_marketing_campaign'] = self.email_marketing_campaign
        kwargs['is_permission_reminder_enabled'] = True
        kwargs['permission_reminder_text'] = reminder_text
        self.email_marketing_campaign = (
            self.cc.update_email_marketing_campaign(**kwargs))
        html, text = self.cc.preview_email_marketing_campaign(
            self.email_marketing_campaign)
        assertIn(self, reminder_text, html)


class EmailMarketingCampaignTests(django.test.TestCase):

    def test_pre_save_works(self):
        """Does pre_save set constant_contact_id?
        """
        data = {'id': 1}
        emc = EmailMarketingCampaign(data=data)
        emc.save()
        self.assertEqual(emc.constant_contact_id, '1')

    def test_pre_delete_fires(self):
        """Is pre_delete wired up correctly?

        If yes, it should raise an exception when we try to delete
        an EmailMarketingCampaign with a bogus constant_contact_id.
        """
        data = {'id': 1}
        emc = EmailMarketingCampaign(data=data)
        emc.save()

        self.assertRaises(ConstantContactAPIError, emc.delete)
