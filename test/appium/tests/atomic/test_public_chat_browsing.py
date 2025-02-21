import random
from datetime import timedelta
from time import sleep

import emoji
import pytest
from dateutil import parser

from tests import marks, test_dapp_name, test_dapp_url
from tests.base_test_case import MultipleDeviceTestCase, create_shared_drivers, \
    MultipleSharedDeviceTestCase
from views.sign_in_view import SignInView
from selenium.common.exceptions import NoSuchElementException


@pytest.mark.xdist_group(name="public_chat_2")
@marks.critical
class TestPublicChatMultipleDeviceMerged(MultipleSharedDeviceTestCase):

    @classmethod
    def setup_class(cls):
        cls.drivers, cls.loop = create_shared_drivers(2)
        device_1, device_2 = SignInView(cls.drivers[0]), SignInView(cls.drivers[1])
        cls.home_1, cls.home_2 = device_1.create_user(), device_2.create_user()
        profile_1 = cls.home_1.profile_button.click()
        cls.username_1 = profile_1.default_username_text.text
        profile_1.home_button.click()
        cls.pub_chat_delete_long_press = 'pub-chat'
        cls.text_message = 'hello'
        cls.home_1.join_public_chat(cls.pub_chat_delete_long_press)
        [home.home_button.click() for home in (cls.home_1, cls.home_2)]
        cls.public_chat_name = cls.home_1.get_random_chat_name()
        cls.chat_1, cls.chat_2 = cls.home_1.join_public_chat(cls.public_chat_name), cls.home_2.join_public_chat(cls.public_chat_name)
        cls.chat_1.send_message(cls.text_message)

    @marks.testrail_id(5313)
    def test_public_chat_message_send_check_timestamps_while_on_different_tab(self):
        message = self.text_message
        self.chat_2.dapp_tab_button.click()
        sent_time_variants = self.chat_1.convert_device_time_to_chat_timestamp()
        timestamp = self.chat_1.chat_element_by_text(message).timestamp_on_tap
        if timestamp not in sent_time_variants:
            self.errors.append("Timestamp is not shown, expected: '%s', in fact: '%s'" % (sent_time_variants.join(','), timestamp))
        self.chat_2.home_button.click(desired_view='chat')
        for chat in self.chat_1, self.chat_2:
            chat.verify_message_is_under_today_text(message, self.errors)
        if self.chat_2.chat_element_by_text(message).username.text != self.username_1:
            self.errors.append("Default username '%s' is not shown next to the received message" % self.username_1)
        self.errors.verify_no_errors()

    @marks.testrail_id(700734)
    def test_public_chat_message_edit(self):
        message_before_edit, message_after_edit = self.text_message, "Message AFTER edit 2"
        self.chat_1.edit_message_in_chat(message_before_edit, message_after_edit)
        for chat in (self.chat_1, self.chat_2):
            if not chat.element_by_text_part("⌫ Edited").is_element_displayed(60):
                self.errors.append('No mark in message bubble about this message was edited')
        if not self.chat_2.element_by_text_part(message_after_edit).is_element_displayed(60):
            self.errors.append('Message is not edited')
        self.errors.verify_no_errors()

    @marks.testrail_id(700735)
    def test_public_chat_message_delete(self):
        message_to_delete = 'delete me, please'
        self.chat_1.send_message(message_to_delete)
        self.chat_1.delete_message_in_chat(message_to_delete)
        for chat in (self.chat_1, self.chat_2):
            if not chat.chat_element_by_text(message_to_delete).is_element_disappeared(30):
                self.errors.append("Deleted message is shown in chat view for public chat")
        self.errors.verify_no_errors()

    @marks.testrail_id(700719)
    def test_public_chat_emoji_send_copy_paste_reply(self):
        emoji_name = random.choice(list(emoji.EMOJI_UNICODE))
        emoji_unicode = emoji.EMOJI_UNICODE[emoji_name]
        emoji_message = emoji.emojize(emoji_name)
        self.chat_1.send_message(emoji_message)
        for chat in self.chat_1, self.chat_2:
            if not chat.chat_element_by_text(emoji_unicode).is_element_displayed(30):
                self.errors.append('Message with emoji was not sent or received in public chat')

        self.chat_1.just_fyi("Can copy and paste emojis")
        self.chat_1.element_by_text_part(emoji_unicode).long_press_element()
        self.chat_1.element_by_text('Copy').click()
        self.chat_1.chat_message_input.paste_text_from_clipboard()
        if self.chat_1.chat_message_input.text != emoji_unicode:
            self.errors.append('Emoji message was not copied')

        self.chat_1.just_fyi("Can reply to emojis")
        self.chat_2.quote_message(emoji_unicode)
        message_text = 'test message'
        self.chat_2.chat_message_input.send_keys(message_text)
        self.chat_2.send_message_button.click()
        chat_element_1 = self.chat_1.chat_element_by_text(message_text)
        if not chat_element_1.is_element_displayed(sec=10) or chat_element_1.replied_message_text != emoji_unicode:
            self.errors.append('Reply message was not received by the sender')
        self.errors.verify_no_errors()

    @marks.testrail_id(5360)
    def test_public_chat_unread_messages_counter(self):
        self.chat_1.send_message('пиу')
        home_1 = self.chat_1.home_button.click()
        message = 'test message'
        self.chat_2.send_message(message)
        if not self.chat_1.home_button.public_unread_messages.is_element_displayed():
            self.errors.append('New messages public chat badge is not shown on Home button')
        chat_element = home_1.get_chat('#' + self.public_chat_name)
        if not chat_element.new_messages_public_chat.is_element_displayed():
            self.errors.append('New messages counter is not shown in public chat')
        self.errors.verify_no_errors()

    @marks.testrail_id(700718)
    def test_public_chat_unread_messages_counter_for_mention_relogin(self):
        message = 'test message2'
        [chat.get_back_to_home_view() for chat in (self.chat_1, self.chat_2)]
        chat_element = self.home_1.get_chat('#' + self.public_chat_name)
        self.home_2.get_chat('#' + self.public_chat_name).click()
        self.chat_2.select_mention_from_suggestion_list(self.username_1, self.username_1[:2])
        self.chat_2.send_message_button.click()
        chat_element.new_messages_counter.wait_for_element(30)
        chat_element.new_messages_counter.wait_for_element_text("1", 60)
        chat_element.click()
        self.home_1.home_button.double_click()
        if self.home_1.home_button.public_unread_messages.is_element_displayed():
            self.errors.append('New messages public chat badge is shown on Home button')
        if chat_element.new_messages_public_chat.is_element_displayed():
            self.errors.append('Unread messages badge is shown in public chat while there are no unread messages')
        [home.get_chat('#' + self.public_chat_name).click() for home in (self.home_1, self.home_2)]
        self.chat_1.send_message(message)
        self.chat_2.chat_element_by_text(message).wait_for_element(20)
        self.home_2.reopen_app()
        chat_element = self.home_2.get_chat('#' + self.public_chat_name)
        if chat_element.new_messages_public_chat.is_element_displayed():
            self.drivers[0].fail('New messages counter is shown after relogin')
        self.errors.verify_no_errors()

    @marks.testrail_id(5319)
    def test_public_chat_delete_chat_long_press(self):
        [chat.get_back_to_home_view() for chat in (self.chat_1, self.chat_2)]
        self.home_1.delete_chat_long_press('#%s' % self.pub_chat_delete_long_press)
        self.home_2.just_fyi("Send message to deleted chat")
        self.deleted_chat_2 = self.home_2.join_public_chat(self.pub_chat_delete_long_press)
        self.deleted_chat_2.send_message()
        if self.home_1.get_chat_from_home_view('#%s' % self.pub_chat_delete_long_press).is_element_displayed():
            self.drivers[0].fail('Deleted public chat reappears after sending message to it')
        self.home_1.reopen_app()
        if self.home_1.get_chat_from_home_view('#%s' % self.pub_chat_delete_long_press).is_element_displayed():
            self.drivers[0].fail('Deleted public chat reappears after relogin')

    @marks.testrail_id(700736)
    def test_public_chat_link_send_open(self):
        [chat.get_back_to_home_view() for chat in (self.chat_1, self.chat_2)]
        [home.get_chat('#' + self.public_chat_name).click() for home in (self.home_1, self.home_2)]
        url_message = 'http://status.im'
        self.chat_2.send_message(url_message)
        self.chat_1.element_starts_with_text(url_message, 'button').click()
        web_view = self.chat_1.open_in_status_button.click()
        if not web_view.element_by_text('Private, Secure Communication').is_element_displayed(60):
            self.drivers[0].fail('URL was not opened from public chat')

    @marks.testrail_id(700737)
    def test_public_chat_links_with_previews_github_youtube_twitter_gif_send_enable(self):
        [chat.get_back_to_home_view() for chat in (self.chat_1, self.chat_2)]
        [home.get_chat('#' + self.public_chat_name).click() for home in (self.home_1, self.home_2)]
        giphy_url = 'https://giphy.com/gifs/this-is-fine-QMHoU66sBXqqLqYvGO'
        preview_urls = {'github_pr': {'url': 'https://github.com/status-im/status-react/pull/11707',
                                      'txt': 'Update translations by jinhojang6 · Pull Request #11707 · status-im/status-react',
                                      'subtitle': 'GitHub'},
                        'yotube': {
                            'url': 'https://www.youtube.com/watch?v=XN-SVmuJH2g&list=PLbrz7IuP1hrgNtYe9g6YHwHO6F3OqNMao',
                            'txt': 'Status & Keycard – Hardware-Enforced Security',
                            'subtitle': 'YouTube'},
                        'twitter': {
                            'url': 'https://twitter.com/ethdotorg/status/1445161651771162627?s=20',
                            'txt': "We've rethought how we translate content, allowing us to translate",
                            'subtitle': 'Twitter'
                        }}

        self.home_1.just_fyi("Check enabling and sending first gif")
        self.chat_2.send_message(giphy_url)
        self.chat_2.element_by_translation_id("dont-ask").click()
        self.chat_1.element_by_translation_id("enable").wait_and_click()
        self.chat_1.element_by_translation_id("enable-all").wait_and_click()
        self.chat_1.close_modal_view_from_chat_button.click()
        if not self.chat_1.get_preview_message_by_text(giphy_url).preview_image:
            self.errors.append("No preview is shown for %s" % giphy_url)
        for key in preview_urls:
            self.home_2.just_fyi("Checking %s preview case" % key)
            data = preview_urls[key]
            self.chat_2.send_message(data['url'])
            message = self.chat_1.get_preview_message_by_text(data['url'])
            if data['txt'] not in message.preview_title.text:
                self.errors.append("Title '%s' does not match expected" % message.preview_title.text)
            if message.preview_subtitle.text != data['subtitle']:
                self.errors.append("Subtitle '%s' does not match expected" % message.preview_subtitle.text)

        self.home_2.just_fyi("Check if after do not ask again previews are not shown and no enable button appear")
        if self.chat_2.element_by_translation_id("enable").is_element_displayed():
            self.errors.append("Enable button is still shown after clicking on 'Den't ask again'")
        if self.chat_2.get_preview_message_by_text(giphy_url).preview_image:
            self.errors.append("Preview is shown for sender without permission")
        self.errors.verify_no_errors()

    @marks.testrail_id(6270)
    def test_public_chat_mark_all_messages_as_read(self):
        [chat.get_back_to_home_view() for chat in (self.chat_1, self.chat_2)]
        self.home_2.get_chat('#' + self.public_chat_name).click()
        self.chat_2.send_message(self.text_message)
        if not self.home_1.home_button.public_unread_messages.is_element_displayed():
            self.errors.append('New messages public chat badge is not shown on Home button')
        chat_element = self.home_1.get_chat('#' + self.public_chat_name)
        if not chat_element.new_messages_public_chat.is_element_displayed():
            self.errors.append('New messages counter is not shown in public chat')
        chat_element.long_press_element()
        self.home_1.mark_all_messages_as_read_button.click()
        self.home_1.home_button.double_click()
        if self.home_1.home_button.public_unread_messages.is_element_displayed():
            self.errors.append('New messages public chat badge is shown on Home button after marking messages as read')
        if chat_element.new_messages_public_chat.is_element_displayed():
            self.errors.append('Unread messages badge is shown in public chat while while there are no unread messages')

        self.errors.verify_no_errors()


@pytest.mark.xdist_group(name="public_chat_browser_1")
@marks.critical
class TestPublicChatBrowserOneDeviceMerged(MultipleSharedDeviceTestCase):

    @classmethod
    def setup_class(cls):
        cls.drivers, cls.loop = create_shared_drivers(1)
        cls.sign_in = SignInView(cls.drivers[0])

        cls.home = cls.sign_in.create_user()
        cls.public_chat_name = cls.home.get_random_chat_name()
        cls.chat = cls.home.join_public_chat(cls.public_chat_name)

    @marks.testrail_id(5675)
    def test_public_chat_fetch_more_history(self):
        self.home.just_fyi("Check that can fetch previous history for several days")
        device_time = parser.parse(self.drivers[0].device_time)
        yesterday = (device_time - timedelta(days=1)).strftime("%b %-d, %Y")
        before_yesterday = (device_time - timedelta(days=2)).strftime("%b %-d, %Y")
        quiet_time_yesterday, quiet_time_before_yesterday = '24 hours', '2 days'
        fetch_more = self.home.get_translation_by_key("load-more-messages")
        for message in (yesterday, quiet_time_yesterday):
            if not self.chat.element_by_text_part(message).is_element_displayed(120):
                self.drivers[0].fail('"%s" is not shown' % message)
        self.chat.element_by_text_part(fetch_more).wait_and_click(120)
        self.chat.element_by_text_part(fetch_more).wait_for_visibility_of_element(180)
        for message in (before_yesterday, quiet_time_before_yesterday):
            if not self.chat.element_by_text_part(message).is_element_displayed():
                self.drivers[0].fail('"%s" is not shown' % message)
        self.home.just_fyi("Check that can fetch previous history for month")
        times = {
            "three-days": '5 days',
            "one-week": '12 days',
            "one-month": ['43 days', '42 days', '41 days', '40 days'],
        }
        profile = self.home.profile_button.click()
        profile.sync_settings_button.click()
        profile.sync_history_for_button.click()
        for period in times:
            profile.just_fyi("Checking %s period" % period)
            profile.element_by_translation_id(period).click()
            profile.home_button.click(desired_view='chat')
            self.chat.element_by_text_part(fetch_more).wait_and_click(120)
            if period != "one-month":
                if not profile.element_by_text_part(times[period]).is_element_displayed(30):
                    self.errors.append("'Quiet here for %s' is not shown after fetching more history" % times[period])
            else:
                variants = times[period]
                self.chat.element_by_text_part(fetch_more).wait_for_invisibility_of_element(120)
                res = any(profile.element_by_text_part(variant).is_element_displayed(30) for variant in variants)
                if not res:
                    self.errors.append("History is not fetched for one month!")
            self.home.profile_button.click(desired_element_text=profile.get_translation_by_key("default-sync-period"))
            self.errors.verify_no_errors()

    @marks.testrail_id(5396)
    def test_public_chat_navigate_to_chat_when_relaunch(self):
        text_message = 'some_text'
        self.home.home_button.double_click()
        self.home.get_chat('#%s' % self.public_chat_name).click()
        self.chat.send_message(text_message)
        self.chat.reopen_app()
        if not self.chat.chat_element_by_text(text_message).is_element_displayed(30):
            self.drivers[0].fail("Not navigated to chat view after reopening app")

    @marks.testrail_id(700738)
    def test_public_chat_tag_message(self):
        tag_message = '#wuuut'
        self.home.home_button.double_click()
        self.home.get_chat('#%s' % self.public_chat_name).click()
        self.home.just_fyi("Check that will be redirected to chat view on tap on tag message")
        self.chat.send_message(tag_message)
        self.chat.element_starts_with_text(tag_message).click()
        self.chat.element_by_text_part(self.public_chat_name).wait_for_invisibility_of_element()
        if not self.chat.user_name_text.text == tag_message:
            self.errors.append('Could not redirect a user to a public chat tapping the tag message.')
        self.home.just_fyi("Check that chat is added to home view")
        self.chat.home_button.double_click()
        if not self.home.element_by_text(tag_message).is_element_displayed():
            self.errors.append('Could not find the public chat in user chat list.')
        self.errors.verify_no_errors()

    @marks.testrail_id(700739)
    def test_public_chat_open_using_deep_link(self):
        self.drivers[0].close_app()
        chat_name = self.home.get_random_chat_name()
        deep_link = 'status-im://%s' % chat_name
        self.sign_in.open_weblink_and_login(deep_link)
        try:
            assert self.chat.user_name_text.text == '#' + chat_name
        except (AssertionError, NoSuchElementException):
            self.driver.fail("Public chat '%s' is not opened" % chat_name)

    @marks.testrail_id(702072)
    def test_browser_blocked_url(self):
        dapp = self.home.dapp_tab_button.click()
        for url in ('metamask.site', 'cryptokitties.domainname'):
            dapp.just_fyi('Checking blocked website %s' % url)
            dapp_detail = dapp.open_url(url)
            dapp_detail.element_by_translation_id('browsing-site-blocked-title')
            if dapp_detail.browser_refresh_page_button.is_element_displayed():
                self.errors.append("Refresh button is present in blocked site")
            dapp_detail.go_back_button.click()
            dapp_detail.open_tabs_button.click()
            dapp.element_by_text_part(url[:8]).click()
            dapp_detail.continue_anyway_button.click()
            if dapp_detail.element_by_text('This site is blocked').is_element_displayed():
                self.errors.append("Failed to open Dapp after 'Continue anyway' tapped for %s" % url)
            dapp_detail.open_tabs_button.click()
            dapp_detail.empty_tab_button.click()
        self.errors.verify_no_errors()

    @marks.testrail_id(702073)
    def test_browser_connection_is_secure_not_secure_warning(self):
        dapp = self.home.dapp_tab_button.click()
        web_page = dapp.open_url('http://www.dvwa.co.uk')
        web_page.url_edit_box_lock_icon.click_until_presence_of_element(
            web_page.element_by_translation_id("browser-not-secure"))
        web_page.open_tabs_button.click()
        web_page.empty_tab_button.click()
        dapp.just_fyi('Checking connection is secure for Airswap')
        web_page = dapp.open_url('https://instant.airswap.io')
        web_page.wait_for_d_aap_to_load()
        web_page.url_edit_box_lock_icon.click_until_presence_of_element(
            web_page.element_by_translation_id("browser-secure"))
        web_page.open_tabs_button.click()
        web_page.empty_tab_button.click()

    @marks.testrail_id(702074)
    def test_browser_invalid_url(self):
        dapp = self.home.dapp_tab_button.click()
        browsing_view = dapp.open_url('invalid.takoe')
        browsing_view.element_by_translation_id("web-view-error").wait_for_element(20)

    @marks.testrail_id(702075)
    def test_browser_offline(self):
        dapp = self.home.dapp_tab_button.click()
        self.home.toggle_airplane_mode()
        browsing_view = dapp.open_url('status.im')
        offline_texts = ['Unable to load page', 'ERR_INTERNET_DISCONNECTED']
        for text in offline_texts:
            browsing_view.element_by_text_part(text).wait_for_element(15)
        self.home.toggle_airplane_mode()
        browsing_view.browser_refresh_page_button.click_until_presence_of_element(
            browsing_view.element_by_text_part('An Open Source Community'))

    @marks.testrail_id(702076)
    def test_browser_delete_close_tabs(self):
        dapp = self.home.dapp_tab_button.click()
        urls = {
            'google.com': 'Google',
            'status.im': 'Status - Private',
            'bbc.com': 'bbc.com'
        }
        for url in urls:
            web_page = dapp.open_url(url)
            web_page.open_tabs_button.click()
            web_page.empty_tab_button.click()

        self.home.just_fyi('Delete one tab')
        web_page.remove_tab(name=urls['bbc.com'])
        if web_page.element_by_text_part(urls['bbc.com']).is_element_displayed():
            self.errors.append('Closed tab is present after deletion')

        self.home.just_fyi('Close all tabs via "Close all", relogin and check that it is not reappearing')
        web_page.close_all_button.click()
        self.home.reopen_app()
        web_page.dapp_tab_button.click()
        web_page.open_tabs_button.click()
        if web_page.element_by_text_part(urls['status.im']).is_element_displayed():
            self.errors.append('Tabs are not closed or reappeared after re-login!')

        self.errors.verify_no_errors()

    @marks.testrail_id(702077)
    def test_browser_bookmarks_create_edit_remove(self):
        dapp = self.home.dapp_tab_button.click()

        self.home.just_fyi('Add some url to bookmarks with default name')
        web_page = dapp.open_url('status.im')
        default_bookmark_name = web_page.add_to_bookmarks()
        web_page.browser_previous_page_button.click()
        if not web_page.element_by_text(default_bookmark_name).is_element_displayed():
            self.errors.append("Bookmark with default name is not added!")

        self.home.just_fyi('Add some url to bookmarks with custom name')
        custom_name = 'Custom BBC'
        dapp.open_url('bbc.com')
        web_page.add_to_bookmarks(custom_name)
        web_page.open_tabs_button.click()
        web_page.empty_tab_button.click()
        if not web_page.element_by_text(custom_name).is_element_displayed():
            self.driver.fail("Bookmark with custom name is not added!")

        self.home.just_fyi('Checking "Open in new tab"')
        dapp.browser_entry_long_press(custom_name)
        dapp.open_in_new_tab_button.click()
        web_page.options_button.click()
        if not web_page.element_by_translation_id('remove-favourite').is_element_displayed():
            self.errors.append("Remove favourite is not shown on added bookmark!")
        dapp.click_system_back_button()

        self.home.just_fyi('Check deleting bookmark')
        web_page.open_tabs_button.click()
        web_page.empty_tab_button.click()
        dapp.browser_entry_long_press(custom_name)
        dapp.delete_bookmark_button.click()
        if web_page.element_by_text(custom_name).is_element_displayed():
            self.errors.append("Bookmark with custom name is not deleted!")

        self.home.just_fyi('Check "Edit bookmark" and "Open in new tab"')
        edited_name = 'My Fav Status'
        dapp.browser_entry_long_press(default_bookmark_name)
        dapp.edit_bookmark_button.click()
        web_page.edit_bookmark_name(edited_name)
        if not web_page.element_by_text(edited_name).is_element_displayed():
            self.driver.fail("Edited bookmark name is not shown!")

        self.errors.verify_no_errors()

    @marks.testrail_id(702078)
    def test_browser_web3_permissions_testdapp(self):
        self.home.home_button.double_click()

        self.home.just_fyi('open Status Test Dapp, allow all and check permissions in Profile')
        web_view = self.home.open_status_test_dapp()
        dapp = self.home.dapp_tab_button.click()
        profile = self.home.profile_button.click()
        profile.privacy_and_security_button.click()
        profile.dapp_permissions_button.click()
        profile.element_by_text(test_dapp_name).click()
        if not profile.element_by_text(self.home.status_account_name).is_element_displayed():
            self.errors.append('Wallet permission was not granted')
        if not profile.element_by_translation_id("chat-key").is_element_displayed():
            self.errors.append('Contact code permission was not granted')

        profile.just_fyi('revoke access and check that they are asked second time')
        profile.revoke_access_button.click()
        profile.back_button.click()
        profile.dapp_tab_button.click()
        web_view.open_tabs_button.click()
        web_view.empty_tab_button.click()
        dapp.open_url(test_dapp_url)
        if not dapp.element_by_text_part(self.home.status_account_name).is_element_displayed():
            self.errors.append('Wallet permission is not asked')
        if dapp.allow_button.is_element_displayed():
            dapp.allow_button.click(times_to_click=1)
        if not dapp.element_by_translation_id("your-contact-code").is_element_displayed():
            self.errors.append('Profile permission is not asked')
        self.errors.verify_no_errors()


class TestPublicChatMultipleDevice(MultipleDeviceTestCase):

    @marks.testrail_id(6342)
    @marks.medium
    def test_different_status_in_timeline(self):
        self.create_drivers(2)
        device_1, device_2 = SignInView(self.drivers[0]), SignInView(self.drivers[1])
        home_1, home_2 = device_1.create_user(), device_2.create_user()
        profile_1, profile_2 = home_1.profile_button.click(), home_2.profile_button.click()
        public_key_1, username_1 = profile_1.get_public_key_and_username(return_username=True)
        emoji_message = random.choice(list(emoji.EMOJI_UNICODE))
        emoji_unicode = emoji.EMOJI_UNICODE[emoji_message]

        home_1.just_fyi('Set status in profile')
        statuses = {
            '*formatted text*': 'formatted text',
            'https://www.youtube.com/watch?v=JjPWmEh2KhA': 'Status Town Hall',
            emoji.emojize(emoji_message): emoji_unicode,

        }
        timeline_1 = device_1.status_button.click()
        for status in statuses.keys():
            timeline_1.set_new_status(status)
            sleep(60)

        timeline_1.element_by_translation_id("enable").wait_and_click()
        timeline_1.element_by_translation_id("enable-all").wait_and_click()
        timeline_1.close_modal_view_from_chat_button.click()
        for status in statuses:
            expected_value = statuses[status]
            if not timeline_1.element_by_text_part(expected_value).is_element_displayed():
                self.errors.append("Expected value %s is not shown" % expected_value)
        text_status = 'some text'
        timeline_1.set_new_status(status=text_status)
        for timestamp in ('Now', '1M', '2M'):
            if not timeline_1.element_by_text(timestamp).is_element_displayed():
                self.errors.append("Expected timestamp %s is not shown in timeline_1" % timestamp)

        home_2.just_fyi('Check that can see user status without adding him as contact')
        profile_2.home_button.click()
        chat_2 = home_2.add_contact(public_key_1, add_in_contacts=False)
        chat_2.chat_options.click()
        chat_2.view_profile_button.click()
        chat_2.chat_element_by_text(text_status).wait_for_element(30)
        chat_2.element_by_translation_id("enable").scroll_and_click()
        chat_2.element_by_translation_id("enable-all").wait_and_click()
        chat_2.close_modal_view_from_chat_button.click()
        for status in statuses:
            chat_2.element_by_text_part(statuses['*formatted text*']).scroll_to_element()
            expected_value = statuses[status]
            if not chat_2.element_by_text_part(expected_value).is_element_displayed():
                self.errors.append(
                    "Expected value %s is not shown in other user profile without adding to contacts" % expected_value)

        home_2.just_fyi('Add device1 to contacts and check that status will be shown in timeline_1')
        chat_2.close_button.scroll_and_click(direction='up')
        chat_2.add_to_contacts.click()
        timeline_2 = chat_2.status_button.click()
        for status in statuses:
            expected_value = statuses[status]
            if not timeline_2.element_by_text_part(expected_value).is_element_displayed():
                self.errors.append(
                    "Expected value %s is not shown in timeline_1 after adding user to contacts" % expected_value)

        profile_1.just_fyi('Checking message tag and reactions on statuses')
        tag_status = '#public-chat-to-redirect-long-name'
        timeline_1.set_new_status(tag_status)
        public_chat_2 = home_2.get_chat_view()

        public_chat_2.element_by_text(tag_status).wait_and_click()
        public_chat_2.user_name_text.wait_for_element(30)
        if not public_chat_2.user_name_text.text == tag_status:
            self.errors.append('Could not redirect a user to a public chat tapping the tag message from timeline_1')
        public_chat_2.back_button.click()

        timeline_1.set_reaction(text_status)
        status_with_reaction_1 = timeline_1.chat_element_by_text(text_status)
        if status_with_reaction_1.emojis_below_message() != 1:
            self.errors.append("Counter of reaction is not updated on your own status in timeline_1!")
        device_2.home_button.double_click()
        home_2.get_chat(username_1).click()
        chat_2.chat_options.click()
        chat_2.view_profile_button.click()
        status_with_reaction_2 = chat_2.chat_element_by_text(text_status)
        if status_with_reaction_2.emojis_below_message(own=False) != 1:
            self.errors.append("Counter of reaction is not updated on status of another user in profile!")
        profile_1.just_fyi("Remove reaction and check it is updated for both users")
        timeline_1.set_reaction(text_status)
        status_with_reaction_1 = timeline_1.chat_element_by_text(text_status)
        if status_with_reaction_1.emojis_below_message() != 0:
            self.errors.append(
                "Counter of reaction is not updated after removing reaction on your own status in timeline_1!")
        status_with_reaction_2 = chat_2.chat_element_by_text(text_status)
        if status_with_reaction_2.emojis_below_message(own=False) != 0:
            self.errors.append(
                "Counter of reaction is not updated after removing on status of another user in profile!")

        profile_1.just_fyi("Remove user from contacts and check there is no his status in timeline_1 anymore")
        chat_2.remove_from_contacts.click()
        chat_2.close_button.click()
        chat_2.status_button.click()
        if public_chat_2.chat_element_by_text(text_status).is_element_displayed(10):
            self.errors.append("Statuses of removed user are still shown in profile")

        self.errors.verify_no_errors()

    @marks.testrail_id(700727)
    @marks.medium
    def test_gap_in_public_chat_and_no_gap_in_1_1_and_group_chats(self):
        self.create_drivers(2)
        device_1, device_2 = SignInView(self.drivers[0]), SignInView(self.drivers[1])
        home_1, home_2 = device_1.create_user(), device_2.create_user()
        message_1 = "testing gap"
        message_2 = "testing no gap"
        pub_chat_name = home_1.get_random_chat_name()
        group_chat_name = home_1.get_random_chat_name()
        public_key_1, username_1 = home_1.get_public_key_and_username(True)
        public_key_2, username_2 = home_2.get_public_key_and_username(True)
        profile_1 = home_1.profile_button.click()
        profile_1.sync_settings_button.click()
        profile_1.sync_history_for_button.click()
        profile_1.element_by_translation_id("two-minutes").click()
        [home.home_button.click() for home in (home_1, home_2)]

        home_1.just_fyi("Creating 1-1 chat and sending message from device 1")
        one_to_one_chat_1 = home_1.add_contact(public_key_2)
        one_to_one_chat_1.send_message("HI")
        home_1.get_back_to_home_view()

        home_1.just_fyi("Creating group chat and sending message from device 1")
        group_chat_1 = home_1.create_group_chat([username_2], group_chat_name)
        group_chat_1.send_message("HI")
        home_1.get_back_to_home_view()

        home_1.just_fyi("Creating public chat and sending message from device 1")
        pub_chat_1, pub_chat_2 = home_1.join_public_chat(pub_chat_name), home_2.join_public_chat(pub_chat_name)
        pub_chat_1.send_message("HI")
        device_1.toggle_airplane_mode()

        home_2.just_fyi("Joining public chat by device 2 and sending message")
        pub_chat_2.send_message(message_1)
        home_2.get_back_to_home_view()

        home_2.just_fyi("Joining 1-1 chat by device 2 and sending message")
        # one_to_one_chat_element = home_2.get_chat(username_1, wait_time=10)
        # one_to_one_chat_2 = one_to_one_chat_element.click()
        one_to_one_chat_2 = home_2.add_contact(public_key_1)
        one_to_one_chat_2.send_message(message_2)
        home_2.get_back_to_home_view()

        home_2.just_fyi("Joining Group chat by device 2 and sending message")
        # home_2.notifications_button.click()
        # group_chat_2 = home_2.get_chat_from_activity_center_view(group_chat_name).click()
        group_chat_2 = home_2.get_chat(group_chat_name).click()
        group_chat_2.join_chat_button.click()
        group_chat_2.send_message(message_2)

        # Waiting for 3 minutes and then going back online
        sleep(180)
        device_1.toggle_airplane_mode()

        home_1.just_fyi("Checking gap in public chat and fetching messages")
        if pub_chat_1.chat_element_by_text(message_1).is_element_displayed(10):
            self.errors.append("Test message has been fetched automatically")
        pub_chat_1.element_by_translation_id("fetch-messages").wait_and_click(60)
        if not pub_chat_1.chat_element_by_text(message_1).is_element_displayed(10):
            self.errors.append("Test message has not been fetched")
        home_1.get_back_to_home_view()

        home_1.just_fyi("Checking that there is no gap in 1-1/group chat and messages fetched automatically")
        for chat in [home_1.get_chat(username_2), home_1.get_chat(group_chat_name)]:
            chat_view = chat.click()
            if chat_view.element_by_translation_id("fetch-messages").is_element_displayed(10):
                self.errors.append("Fetch messages button is displayed in {}} chat".format(chat.user_name_text.text))
            if not chat_view.chat_element_by_text(message_2).is_element_displayed(10):
                self.errors.append("Message in {} chat has not been fetched automatically".format(chat.user_name_text.text))
            chat_view.back_button.click()
        self.errors.verify_no_errors()



