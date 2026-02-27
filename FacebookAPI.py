"""
╔══════════════════════════════════════════════════════════════════╗
║              API FACEBOOK (UNOFFICIAL)                          ║
╠══════════════════════════════════════════════════════════════════╣
║  Các API này dùng COOKIE (lấy từ trình duyệt), KHÔNG dùng       ║
║  Access Token của Graph API.                                     ║
║                                                                  ║
║  Cơ chế hoạt động:                                              ║
║    1. Dùng Cookie để truy cập Facebook như trình duyệt thật      ║
║    2. Tự động lấy fb_dtsg, lsd, jazoest từ trang HTML            ║
║    3. Gọi endpoint nội bộ: https://www.facebook.com/api/graphql/ ║
║                                                                  ║
║  Cách lấy Cookie:                                                ║
║    Mở F12 → Network → Vào facebook.com → Copy header "Cookie"   ║
║    Hoặc dùng EditThisCookie extension trên Chrome                ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║                                    author: Đạt Thành - pillrock  ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ──────────────────────────────────────────────────────────────────
# KẾT QUẢ CHẠY THỬ (TEST RESULT)
# 1.  info()                  ✅ - Lần cuối 20/2/2026
# 2.  reaction()              ✅ - Lần cuối 20/2/2026
# 3.  reaction_comment()      ✅ - Lần cuối 20/2/2026
# 4.  share()                 ✅ - Lần cuối 22/2/2026
# 5.  share_with_message()    ✅ - Lần cuối 21/2/2026
# 6.  rate_page()             ✅ - Lần cuối 21/2/2026
# 7.  comment()               ✅ - Lần cuối 20/2/2026
# 8.  follow()                ✅ - Lần cuối 20/2/2026
# 9.  join_page()             ✅ - Lần cuối 20/2/2026
# 10. like_page()             ✅ - Lần cuối 20/2/2026
# ──────────────────────────────────────────────────────────────────


import requests
import re
import uuid
import base64
from datetime import datetime


# ──────────────────────────────────────────────────────────────────
# TIỆN ÍCH
# ──────────────────────────────────────────────────────────────────

def encode_base64(text: str) -> str:
    """Encode chuỗi sang Base64 (dùng nội bộ cho reaction ID)."""
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")


# ──────────────────────────────────────────────────────────────────
# LỚP CHÍNH: FACEBOOK API (Cookie-based)
# ──────────────────────────────────────────────────────────────────

class FacebookAPI:
    """
    Facebook Internal API dùng Cookie.

    Khởi tạo với chuỗi Cookie lấy từ trình duyệt.
    Tự động parse các token bảo mật: fb_dtsg, lsd, jazoest.

    Ví dụ:
        fb = FacebookAPI("c_user=123456; xs=abc123; ...")
        print(fb.info())
    """

    # Bản đồ reaction type → feedback_reaction_id nội bộ của FB
    REACTION_IDS = {
        "LIKE":  "1635855486666999",
        "LOVE":  "1678524932434102",
        "CARE":  "613557422527858",
        "HAHA":  "115940658764963",
        "WOW":   "478547315650144",
        "SAD":   "908563459236466",
        "ANGRY": "444813342392137",
    }

    def __init__(self, cookie: str, proxy: str = None):
        """
        Khởi tạo FacebookAPI với Cookie.

        Args:
            cookie: Chuỗi Cookie đầy đủ từ trình duyệt.
                    Phải chứa 'c_user=...' để lấy user ID.
            proxy:  (Tùy chọn) Proxy dạng "host:port:user:pass"
        """
        self.cookie   = cookie
        self.fb_dtsg  = ""
        self.jazoest  = ""
        self.lsd      = ""
        self.proxies  = None

        # Lấy actor_id (UID) từ cookie
        try:
            self.actor_id = cookie.split("c_user=")[1].split(";")[0].strip()
        except IndexError:
            raise ValueError("Cookie không hợp lệ! Thiếu trường 'c_user'.")

        # Cấu hình header giả lập trình duyệt
        self.headers = {
            "authority":        "www.facebook.com",
            "accept":           "*/*",
            "cookie":           self.cookie,
            "origin":           "https://www.facebook.com",
            "referer":          "https://www.facebook.com/",
            "sec-fetch-dest":   "empty",
            "sec-fetch-mode":   "cors",
            "sec-fetch-site":   "same-origin",
            "user-agent":       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/120.0.0.0 Safari/537.36",
        }

        # Khởi tạo proxy nếu có
        if proxy:
            try:
                parts = proxy.strip().split(":")
                if len(parts) == 4:
                    host, port, user, password = parts
                    self.proxies = {
                        "http":  f"http://{user}:{password}@{host}:{port}",
                        "https": f"http://{user}:{password}@{host}:{port}",
                    }
            except Exception as e:
                print(f"⚠️ Lỗi proxy, bỏ qua: {e}")

        # Tự động lấy các token bảo mật từ trang Facebook
        self._fetch_tokens()

    def _fetch_tokens(self):
        """
        Lấy fb_dtsg, lsd, jazoest từ trang profile Facebook.
        Các token này cần thiết cho mọi request GraphQL nội bộ.
        """
        try:
            url = requests.get(
                f"https://www.facebook.com/{self.actor_id}",
                headers=self.headers,
                proxies=self.proxies,
                timeout=15
            ).url

            html = requests.get(
                url,
                headers=self.headers,
                proxies=self.proxies,
                timeout=15
            ).text

            dtsg_match = re.findall(r'\["DTSGInitialData",\[\],\{"token":"(.*?)"\}', html)
            if dtsg_match:
                self.fb_dtsg = dtsg_match[0]
                self.jazoest = re.findall(r'jazoest=(.*?)\"', html)[0]
                self.lsd     = re.findall(r'\["LSD",\[\],\{"token":"(.*?)"\}', html)[0]
        except Exception as e:
            print(f"⚠️ Không lấy được token bảo mật: {e}")

    # ──────────────────────────────────────────────────────────────
    # THÔNG TIN TÀI KHOẢN
    # ──────────────────────────────────────────────────────────────

    def info(self) -> dict:
        """
        Lấy tên và ID tài khoản. Dùng để kiểm tra cookie còn sống không.

        Returns:
            {'success': 200, 'id': '...', 'name': '...'}  nếu OK
            {'error': 200}  nếu cookie die
        """
        try:
            html = requests.get(
                "https://www.facebook.com/me",
                headers=self.headers,
                proxies=self.proxies,
                timeout=15
            ).text
            name = html.split("<title>")[1].split("</title>")[0]
            return {"success": 200, "id": self.actor_id, "name": name}
        except:
            return {"error": 200}

    # ──────────────────────────────────────────────────────────────
    # BÀY TỎ CẢM XÚC BÀI VIẾT (REACT POST)
    # ──────────────────────────────────────────────────────────────

    def reaction(self, post_id: str, reaction_type: str = "LIKE") -> bool:
        """
        Bày tỏ cảm xúc cho một bài viết trên News Feed.

        Endpoint nội bộ: POST /api/graphql/ (CometUFIFeedbackReactMutation)

        Args:
            post_id:       ID bài viết (chỉ cần phần số, ví dụ: "1107132327795370")
                           Nếu truyền dạng "user_post", tự động tách post ID.
            reaction_type: LIKE | LOVE | CARE | HAHA | WOW | SAD | ANGRY

        Returns:
            True nếu thành công, False nếu thất bại.
        """
        reaction_type = reaction_type.upper()
        if reaction_type not in self.REACTION_IDS:
            print(f"❌ Reaction '{reaction_type}' không hợp lệ. Chọn: {list(self.REACTION_IDS.keys())}")
            return False

        # Tách post_id nếu có định dạng "user_post"
        if "_" in post_id:
            post_id = post_id.split("_")[1]

        reaction_id = self.REACTION_IDS[reaction_type]
        feedback_id = encode_base64(f"feedback:{post_id}")

        data = {
            "av":                          self.actor_id,
            "__user":                      self.actor_id,
            "__a":                         "1",
            "__hs":                        "19896.HYP:comet_pkg.2.1..2.1",
            "dpr":                         "1",
            "__ccg":                       "EXCELLENT",
            "__rev":                       "1014402108",
            "fb_dtsg":                     self.fb_dtsg,
            "jazoest":                     self.jazoest,
            "lsd":                         self.lsd,
            "fb_api_caller_class":         "RelayModern",
            "fb_api_req_friendly_name":    "CometUFIFeedbackReactMutation",
            "variables": (
                f'{{"input":{{'
                f'"attribution_id_v2":"CometHomeRoot.react,comet.home,tap_tabbar,'
                f'1719027162723,322693,4748854339,,",'
                f'"feedback_id":"{feedback_id}",'
                f'"feedback_reaction_id":"{reaction_id}",'
                f'"feedback_source":"NEWS_FEED",'
                f'"is_tracking_encrypted":true,'
                f'"tracking":[],'
                f'"session_id":"{uuid.uuid4()}",'
                f'"actor_id":"{self.actor_id}",'
                f'"client_mutation_id":"3"}},'
                f'"useDefaultActor":false,'
                f'"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}}'
            ),
            "server_timestamps": "true",
            "doc_id":            "7047198228715224",
        }

        try:
            response = requests.post(
                "https://www.facebook.com/api/graphql/",
                headers=self.headers,
                data=data,
                proxies=self.proxies,
                timeout=15
            )
        except Exception:
            return False

        if '{"data":{"feedback_react":{"feedback":{"id":' in response.text:
            return True
        return False

    # ──────────────────────────────────────────────────────────────
    # BÀY TỎ CẢM XÚC COMMENT (REACT COMMENT)
    # ──────────────────────────────────────────────────────────────

    def reaction_comment(self, comment_id: str, reaction_type: str = "LIKE") -> bool:
        """
        Bày tỏ cảm xúc cho một comment (bình luận).

        Endpoint nội bộ: POST /api/graphql/ (CometUFIFeedbackReactMutation)
        doc_id khác với reaction thông thường.

        Args:
            comment_id:    ID của comment cần react.
            reaction_type: LIKE | LOVE | CARE | HAHA | WOW | SAD | ANGRY

        Returns:
            True nếu thành công, False nếu thất bại.
        """
        reaction_type = reaction_type.upper()
        if reaction_type not in self.REACTION_IDS:
            print(f"❌ Reaction '{reaction_type}' không hợp lệ.")
            return False

        if "_" in comment_id:
            comment_id = comment_id.split("_")[1]

        reaction_id = self.REACTION_IDS[reaction_type]
        feedback_id = encode_base64(f"feedback:{comment_id}")

        # Lấy timestamp hiện tại cho downstream_share_session_start_time
        now = datetime.now()
        timestamp = str(now.timestamp()).replace(".", "")

        data = {
            "av":                          self.actor_id,
            "__user":                      self.actor_id,
            "__a":                         "1",
            "__hs":                        "19906.HYP:comet_pkg.2.1..2.1",
            "dpr":                         "1",
            "__ccg":                       "GOOD",
            "__rev":                       "1014619389",
            "fb_dtsg":                     self.fb_dtsg,
            "jazoest":                     self.jazoest,
            "lsd":                         self.lsd,
            "fb_api_caller_class":         "RelayModern",
            "fb_api_req_friendly_name":    "CometUFIFeedbackReactMutation",
            "variables": (
                f'{{"input":{{'
                f'"attribution_id_v2":"CometVideoHomeNewPermalinkRoot.react,'
                f'comet.watch.injection,via_cold_start,{timestamp},975645,2392950137,,",'
                f'"feedback_id":"{feedback_id}",'
                f'"feedback_reaction_id":"{reaction_id}",'
                f'"feedback_source":"TAHOE",'
                f'"is_tracking_encrypted":true,'
                f'"tracking":[],'
                f'"session_id":"{uuid.uuid4()}",'
                f'"downstream_share_session_id":"{uuid.uuid4()}",'
                f'"downstream_share_session_start_time":"{timestamp}",'
                f'"actor_id":"{self.actor_id}",'
                f'"client_mutation_id":"1"}},'
                f'"useDefaultActor":false,'
                f'"__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":false}}'
            ),
            "server_timestamps": "true",
            "doc_id":            "7616998081714004",  # ← khác với reaction post
        }

        try:
            response = requests.post(
                "https://www.facebook.com/api/graphql/",
                headers=self.headers,
                data=data,
                proxies=self.proxies,
                timeout=15
            )
        except Exception:
            return False

        if '{"data":{"feedback_react":{"feedback":{"id":' in response.text:
            return True
        return False

    # ──────────────────────────────────────────────────────────────
    # CHIA SẺ BÀI VIẾT (SHARE)
    # ──────────────────────────────────────────────────────────────

    def share(self, post_id: str) -> bool:
        """
        Chia sẻ một bài viết lên tường cá nhân (News Feed).

        Endpoint nội bộ: POST /api/graphql/ (ComposerStoryCreateMutation)

        Args:
            post_id: ID bài viết cần share (phần số).
                     Nếu dạng "user_post", tự động tách.
                     Ví dụ: "3342889705874501"

        Returns:
            True nếu thành công, False nếu thất bại.

        Cập nhật 2026-02-20: doc_id và variables lấy từ request thật.
        """
        import json as _json

        if "_" in post_id:
            post_id = post_id.split("_")[1]

        session_id = str(uuid.uuid4())
        idempotence_token = f"{uuid.uuid4()}_FEED"

        # Cấu trúc share_scrape_data phải là string JSON escaped bên trong
        share_scrape_data = f'{{"share_type":22,"share_params":[{post_id}]}}'

        variables = {
            "input": {
                "composer_entry_point": "share_modal",
                "composer_source_surface": "feed_story",
                "composer_type": "share",
                "idempotence_token": idempotence_token,
                "source": "WWW",
                "attachments": [{"link": {"share_scrape_data": share_scrape_data}}],
                "reshare_original_post": "RESHARE_ORIGINAL_POST",
                "audience": {
                    "privacy": {
                        "allow": [],
                        "base_state": "EVERYONE",
                        "deny": [],
                        "tag_expansion_state": "UNSPECIFIED"
                    }
                },
                "is_tracking_encrypted": True,
                "tracking": [],
                "message": {"ranges": [], "text": ""},
                "logging": {"composer_session_id": session_id},
                "navigation_data": {
                    "attribution_id_v2": "CometHomeRoot.react,comet.home,logo,1771589928257,152156,4748854339,,"
                },
                "event_share_metadata": {"surface": "newsfeed"},
                "actor_id": self.actor_id,
                "client_mutation_id": "2"
            },
            "feedLocation": "NEWSFEED",
            "feedbackSource": 1,
            "focusCommentID": None,
            "gridMediaWidth": None,
            "groupID": None,
            "scale": 1,
            "privacySelectorRenderLocation": "COMET_STREAM",
            "checkPhotosToReelsUpsellEligibility": False,
            "referringStoryRenderLocation": None,
            "renderLocation": "homepage_stream",
            "useDefaultActor": False,
            "inviteShortLinkKey": None,
            "isFeed": True,
            "isFundraiser": False,
            "isFunFactPost": False,
            "isGroup": False,
            "isEvent": False,
            "isTimeline": False,
            "isSocialLearning": False,
            "isPageNewsFeed": False,
            "isProfileReviews": False,
            "isWorkSharedDraft": False,
            "hashtag": None,
            "canUserManageOffers": False,
            # Các relay provider flags (lấy từ request thật 2026-02-20)
            "__relay_internal__pv__CometUFIShareActionMigrationrelayprovider": True,
            "__relay_internal__pv__GHLShouldChangeSponsoredDataFieldNamerelayprovider": True,
            "__relay_internal__pv__GHLShouldChangeAdIdFieldNamerelayprovider": True,
            "__relay_internal__pv__CometUFI_dedicated_comment_routable_dialog_gkrelayprovider": False,
            "__relay_internal__pv__CometUFICommentAvatarStickerAnimatedImagerelayprovider": False,
            "__relay_internal__pv__CometUFICommentActionLinksRewriteEnabledrelayprovider": False,
            "__relay_internal__pv__IsWorkUserrelayprovider": False,
            "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False,
            "__relay_internal__pv__CometUFISingleLineUFIrelayprovider": False,
            "__relay_internal__pv__TestPilotShouldIncludeDemoAdUseCaserelayprovider": False,
            "__relay_internal__pv__FBReels_deprecate_short_form_video_context_gkrelayprovider": True,
            "__relay_internal__pv__FBReels_enable_view_dubbed_audio_type_gkrelayprovider": True,
            "__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider": False,
            "__relay_internal__pv__WorkCometIsEmployeeGKProviderrelayprovider": False,
            "__relay_internal__pv__IsMergQAPollsrelayprovider": False,
            "__relay_internal__pv__FBReels_enable_meta_ai_label_gkrelayprovider": True,
            "__relay_internal__pv__FBReelsMediaFooter_comet_enable_reels_ads_gkrelayprovider": True,
            "__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider": True,
            "__relay_internal__pv__FBReelsIFUTileContent_reelsIFUPlayOnHoverrelayprovider": True,
            "__relay_internal__pv__GroupsCometGYSJFeedItemHeightrelayprovider": 206,
            "__relay_internal__pv__ShouldEnableBakedInTextStoriesrelayprovider": False,
            "__relay_internal__pv__StoriesShouldIncludeFbNotesrelayprovider": False,
            "__relay_internal__pv__groups_comet_use_glvrelayprovider": True,
            "__relay_internal__pv__GHLShouldChangeSponsoredAuctionDistanceFieldNamerelayprovider": True,
            "__relay_internal__pv__GHLShouldUseSponsoredAuctionLabelFieldNameV1relayprovider": False,
            "__relay_internal__pv__GHLShouldUseSponsoredAuctionLabelFieldNameV2relayprovider": True,
        }

        data = {
            "av":                          self.actor_id,
            "__user":                      self.actor_id,
            "__a":                         "1",
            "__hs":                        "20506.HCSV2:comet_pkg.2.1...0",
            "dpr":                         "1",
            "__ccg":                       "EXCELLENT",
            "__rev":                       "1033852585",
            "fb_dtsg":                     self.fb_dtsg,
            "jazoest":                     self.jazoest,
            "lsd":                         self.lsd,
            "fb_api_caller_class":         "RelayModern",
            "fb_api_req_friendly_name":    "ComposerStoryCreateMutation",
            "variables":                   _json.dumps(variables),
            "server_timestamps":           "true",
            "doc_id":                      "26264075519853494",     # ⚠️ Cập nhật 2026-02-22
        }

        # Header bổ sung từ request thật
        headers = {
            **self.headers,
            "content-type":           "application/x-www-form-urlencoded",
            "x-fb-lsd":               self.lsd,
            "x-fb-friendly-name":     "ComposerStoryCreateMutation",
            "x-asbd-id":              "359341",
        }

        try:
            response = requests.post(
                "https://www.facebook.com/api/graphql/",
                headers=headers,
                data=data,
                proxies=self.proxies,
                timeout=15
            )
        except Exception:
            return False

        # Kiểm tra text trước, tránh crash khi response rỗng hoặc redirect
        if not response.text or '"errors"' not in response.text:
            return True

        # Có "errors" → parse JSON để lấy thêm thông tin
        try:
            resp_json = response.json()
            for err in resp_json.get("errors", []):
                if err.get("severity") == "CRITICAL":
                    break
        except Exception:
            pass
        return False

    # ──────────────────────────────────────────────────────────────
    # CHIA SẺ BÀI VIẾT KÈM NỘI DUNG (SHARE WITH MESSAGE)
    # ──────────────────────────────────────────────────────────────

    def share_with_message(self, post_id: str, message: str = "") -> bool:
        """
        Chia sẻ một bài viết lên tường cá nhân kèm nội dung (caption).

        Endpoint nội bộ: POST /api/graphql/ (ComposerStoryCreateMutation)

        Khác với share() ở chỗ:
            - Truyền thêm nội dung caption vào trường message.text
            - doc_id mới lấy từ request thật (2026-02-21)
            - surface = "timeline" (thay vì "newsfeed")

        Args:
            post_id: ID bài viết cần share (phần số thuần).
                     Nếu dạng "user_post", tự động tách.
                     Ví dụ: "122115153717187122"
            message: Nội dung caption muốn kèm khi share.
                     Ví dụ: "Hay quá! 🔥"
                     Mặc định là "" (share không kèm nội dung → giống share()).

        Returns:
            True nếu thành công, False nếu thất bại.

        Cập nhật 2026-02-21: doc_id lấy từ request thật (ComposerStoryCreateMutation).
        """
        import json as _json

        if "_" in post_id:
            post_id = post_id.split("_")[1]

        session_id       = str(uuid.uuid4())
        idempotence_token = f"{uuid.uuid4()}_FEED"

        share_scrape_data = f'{{"share_type":22,"share_params":[{post_id}]}}'

        variables = {
            "input": {
                "composer_entry_point": "share_modal",
                "composer_source_surface": "feed_story",
                "composer_type": "share",
                "idempotence_token": idempotence_token,
                "source": "WWW",
                "attachments": [{"link": {"share_scrape_data": share_scrape_data}}],
                "reshare_original_post": "RESHARE_ORIGINAL_POST",
                "audience": {
                    "privacy": {
                        "allow": [],
                        "base_state": "EVERYONE",
                        "deny": [],
                        "tag_expansion_state": "UNSPECIFIED",
                    }
                },
                "is_tracking_encrypted": True,
                "tracking": [],
                # ← Đây là điểm khác biệt chính so với share()
                "message": {"ranges": [], "text": message},
                "logging": {"composer_session_id": session_id},
                "navigation_data": {
                    "attribution_id_v2": (
                        f"ProfileCometTimelineListViewRoot.react,"
                        f"comet.profile.timeline.list,unexpected,"
                        f"1771650963547,198694,{self.actor_id},,;"
                        f"ProfileCometTimelineListViewRoot.react,"
                        f"comet.profile.timeline.list,tap_bookmark,"
                        f"1771650957795,89632,{self.actor_id},"
                        f"304#10#230#340#301,"
                    )
                },
                # ← surface = "timeline" thay vì "newsfeed"
                "event_share_metadata": {"surface": "timeline"},
                "actor_id": self.actor_id,
                "client_mutation_id": "2",
            },
            "feedLocation": "NEWSFEED",
            "feedbackSource": 1,
            "focusCommentID": None,
            "gridMediaWidth": None,
            "groupID": None,
            "scale": 1,
            "privacySelectorRenderLocation": "COMET_STREAM",
            "checkPhotosToReelsUpsellEligibility": False,
            "referringStoryRenderLocation": None,
            "renderLocation": "homepage_stream",
            "useDefaultActor": False,
            "inviteShortLinkKey": None,
            "isFeed": True,
            "isFundraiser": False,
            "isFunFactPost": False,
            "isGroup": False,
            "isEvent": False,
            "isTimeline": False,
            "isSocialLearning": False,
            "isPageNewsFeed": False,
            "isProfileReviews": False,
            "isWorkSharedDraft": False,
            "hashtag": None,
            "canUserManageOffers": False,
            "__relay_internal__pv__CometUFIShareActionMigrationrelayprovider": True,
            "__relay_internal__pv__GHLShouldChangeSponsoredDataFieldNamerelayprovider": True,
            "__relay_internal__pv__GHLShouldChangeAdIdFieldNamerelayprovider": True,
            "__relay_internal__pv__CometUFI_dedicated_comment_routable_dialog_gkrelayprovider": False,
            "__relay_internal__pv__CometUFICommentAvatarStickerAnimatedImagerelayprovider": False,
            "__relay_internal__pv__CometUFICommentActionLinksRewriteEnabledrelayprovider": False,
            "__relay_internal__pv__IsWorkUserrelayprovider": False,
            "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider": False,
            "__relay_internal__pv__CometUFISingleLineUFIrelayprovider": False,
            "__relay_internal__pv__TestPilotShouldIncludeDemoAdUseCaserelayprovider": False,
            "__relay_internal__pv__FBReels_deprecate_short_form_video_context_gkrelayprovider": True,
            "__relay_internal__pv__FBReels_enable_view_dubbed_audio_type_gkrelayprovider": True,
            "__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider": False,
            "__relay_internal__pv__WorkCometIsEmployeeGKProviderrelayprovider": False,
            "__relay_internal__pv__IsMergQAPollsrelayprovider": False,
            "__relay_internal__pv__FBReels_enable_meta_ai_label_gkrelayprovider": True,
            "__relay_internal__pv__FBReelsMediaFooter_comet_enable_reels_ads_gkrelayprovider": True,
            "__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider": True,
            "__relay_internal__pv__FBReelsIFUTileContent_reelsIFUPlayOnHoverrelayprovider": True,
            "__relay_internal__pv__GroupsCometGYSJFeedItemHeightrelayprovider": 206,
            "__relay_internal__pv__ShouldEnableBakedInTextStoriesrelayprovider": False,
            "__relay_internal__pv__StoriesShouldIncludeFbNotesrelayprovider": False,
            "__relay_internal__pv__groups_comet_use_glvrelayprovider": False,
            "__relay_internal__pv__GHLShouldChangeSponsoredAuctionDistanceFieldNamerelayprovider": False,
            "__relay_internal__pv__GHLShouldUseSponsoredAuctionLabelFieldNameV1relayprovider": False,
            "__relay_internal__pv__GHLShouldUseSponsoredAuctionLabelFieldNameV2relayprovider": False,
        }

        data = {
            "av":                          self.actor_id,
            "__user":                      self.actor_id,
            "__a":                         "1",
            "__hs":                        "20505.HCSV2:comet_pkg.2.1...0",
            "dpr":                         "1",
            "__ccg":                       "EXCELLENT",
            "__rev":                       "1033825359",
            "fb_dtsg":                     self.fb_dtsg,
            "jazoest":                     self.jazoest,
            "lsd":                         self.lsd,
            "fb_api_caller_class":         "RelayModern",
            "fb_api_req_friendly_name":    "ComposerStoryCreateMutation",
            "variables":                   _json.dumps(variables),
            "server_timestamps":           "true",
            "doc_id":                      "25890641460638978",  # ⚠️ Cập nhật 2026-02-21
        }

        headers = {
            **self.headers,
            "content-type":           "application/x-www-form-urlencoded",
            "x-fb-lsd":               self.lsd,
            "x-fb-friendly-name":     "ComposerStoryCreateMutation",
            "x-asbd-id":              "359341",
            "referer":                f"https://www.facebook.com/profile.php?id={self.actor_id}",
        }

        try:
            response = requests.post(
                "https://www.facebook.com/api/graphql/",
                headers=headers,
                data=data,
                proxies=self.proxies,
                timeout=15
            )
        except Exception:
            return False

        if not response.text or '"errors"' not in response.text:
            return True

        try:
            resp_json = response.json()
            for err in resp_json.get("errors", []):
                if err.get("severity") == "CRITICAL":
                    # print(f"   ⚠️ Lỗi share_with_message: {err.get('description', err.get('message', ''))}")
                    return False
        except Exception:
            pass
        return False

    # ──────────────────────────────────────────────────────────────
    # ĐÁNH GIÁ TRANG (RATE PAGE)
    # ──────────────────────────────────────────────────────────────

    def rate_page(self, page_id: str, text: str, rec_type: str = "POSITIVE") -> bool:
        """
        Đánh giá (rate/review) một Facebook Page.

        Endpoint nội bộ: POST /api/graphql/ (ComposerStoryCreateMutation)

        Args:
            page_id:  ID số của trang cần đánh giá.
                      Ví dụ: "532762067182594"
            text:     Nội dung đánh giá.
                      Ví dụ: "Nhân viên thân thiện, không gian đẹp!"
            rec_type: Loại đánh giá:
                        "POSITIVE" → đánh giá tích cực (👍, mặc định)
                        "NEGATIVE" → đánh giá tiêu cực (👎)

        Returns:
            True nếu đánh giá thành công, False nếu thất bại.

        Cập nhật 2026-02-21: doc_id và variables lấy từ request thật.
        """
        import json as _json

        rec_type = rec_type.upper()
        if rec_type not in ("POSITIVE", "NEGATIVE"):
            print("❌ rec_type phải là 'POSITIVE' hoặc 'NEGATIVE'")
            return False

        session_id        = str(uuid.uuid4())
        idempotence_token = f"{uuid.uuid4()}_FEED"

        variables = {
            "input": {
                "composer_entry_point":    "inline_composer",
                "composer_source_surface": "page_recommendation_tab",
                "idempotence_token":       idempotence_token,
                "source":                  "WWW",
                "audience": {
                    "privacy": {
                        "allow":              [],
                        "base_state":         "EVERYONE",
                        "deny":               [],
                        "tag_expansion_state": "UNSPECIFIED",
                    }
                },
                "message":              {"ranges": [], "text": text},
                "with_tags_ids":        None,
                "text_format_preset_id": "0",
                # ← Field quan trọng: chứa page_id và loại đánh giá
                "page_recommendation": {
                    "page_id":  page_id,
                    "rec_type": rec_type,
                },
                "logging":          {"composer_session_id": session_id},
                "navigation_data":  {
                    "attribution_id_v2": (
                        f"ProfileCometReviewsTabRoot.react,"
                        f"comet.profile.reviews,unexpected,"
                        f"1771651461028,277212,250100865708545,,;"
                        f"ProfileCometMentionsTabWithDeepDiveRoot.react,"
                        f"comet.profile.mentions,unexpected,"
                        f"1771651443578,534635,250100865708545,,"
                    )
                },
                "tracking":            [None],
                "event_share_metadata": {"surface": "newsfeed"},
                "actor_id":            self.actor_id,
                "client_mutation_id":  "6",
            },
            "feedLocation":                       "PAGE_SURFACE_RECOMMENDATIONS",
            "feedbackSource":                     0,
            "focusCommentID":                     None,
            "gridMediaWidth":                     None,
            "groupID":                            None,
            "scale":                              1,
            "privacySelectorRenderLocation":      "COMET_STREAM",
            "checkPhotosToReelsUpsellEligibility": False,
            "referringStoryRenderLocation":       None,
            "renderLocation":                     "timeline",
            "useDefaultActor":                    False,
            "inviteShortLinkKey":                 None,
            "isFeed":                             False,
            "isFundraiser":                       False,
            "isFunFactPost":                      False,
            "isGroup":                            False,
            "isEvent":                            False,
            "isTimeline":                         True,   # ← khác share()
            "isSocialLearning":                   False,
            "isPageNewsFeed":                     False,
            "isProfileReviews":                   True,   # ← khác share()
            "isWorkSharedDraft":                  False,
            "hashtag":                            None,
            "canUserManageOffers":                False,
            "__relay_internal__pv__CometUFIShareActionMigrationrelayprovider":              True,
            "__relay_internal__pv__GHLShouldChangeSponsoredDataFieldNamerelayprovider":     True,
            "__relay_internal__pv__GHLShouldChangeAdIdFieldNamerelayprovider":              True,
            "__relay_internal__pv__CometUFI_dedicated_comment_routable_dialog_gkrelayprovider": False,
            "__relay_internal__pv__CometUFICommentAvatarStickerAnimatedImagerelayprovider": False,
            "__relay_internal__pv__CometUFICommentActionLinksRewriteEnabledrelayprovider":  False,
            "__relay_internal__pv__IsWorkUserrelayprovider":                                False,
            "__relay_internal__pv__CometUFIReactionsEnableShortNamerelayprovider":          False,
            "__relay_internal__pv__CometUFISingleLineUFIrelayprovider":                     False,
            "__relay_internal__pv__TestPilotShouldIncludeDemoAdUseCaserelayprovider":       False,
            "__relay_internal__pv__FBReels_deprecate_short_form_video_context_gkrelayprovider": True,
            "__relay_internal__pv__FBReels_enable_view_dubbed_audio_type_gkrelayprovider":  True,
            "__relay_internal__pv__CometImmersivePhotoCanUserDisable3DMotionrelayprovider": False,
            "__relay_internal__pv__WorkCometIsEmployeeGKProviderrelayprovider":             False,
            "__relay_internal__pv__IsMergQAPollsrelayprovider":                             False,
            "__relay_internal__pv__FBReels_enable_meta_ai_label_gkrelayprovider":           True,
            "__relay_internal__pv__FBReelsMediaFooter_comet_enable_reels_ads_gkrelayprovider": True,
            "__relay_internal__pv__StoriesArmadilloReplyEnabledrelayprovider":              True,
            "__relay_internal__pv__FBReelsIFUTileContent_reelsIFUPlayOnHoverrelayprovider": True,
            "__relay_internal__pv__GroupsCometGYSJFeedItemHeightrelayprovider":             206,
            "__relay_internal__pv__ShouldEnableBakedInTextStoriesrelayprovider":            False,
            "__relay_internal__pv__StoriesShouldIncludeFbNotesrelayprovider":               False,
            "__relay_internal__pv__groups_comet_use_glvrelayprovider":                      False,
            "__relay_internal__pv__GHLShouldChangeSponsoredAuctionDistanceFieldNamerelayprovider": False,
            "__relay_internal__pv__GHLShouldUseSponsoredAuctionLabelFieldNameV1relayprovider": False,
            "__relay_internal__pv__GHLShouldUseSponsoredAuctionLabelFieldNameV2relayprovider": False,
        }

        data = {
            "av":                          self.actor_id,
            "__user":                      self.actor_id,
            "__a":                         "1",
            "__hs":                        "20505.HCSV2:comet_pkg.2.1...0",
            "dpr":                         "1",
            "__ccg":                       "EXCELLENT",
            "__rev":                       "1033825359",
            "fb_dtsg":                     self.fb_dtsg,
            "jazoest":                     self.jazoest,
            "lsd":                         self.lsd,
            "qpl_active_flow_ids":         "431626709",            # ← có trong curl thật
            "fb_api_caller_class":         "RelayModern",
            "fb_api_req_friendly_name":    "ComposerStoryCreateMutation",
            "variables":                   _json.dumps(variables),
            "server_timestamps":           "true",
            "doc_id":                      "25890641460638978",
            "fb_api_analytics_tags":       '["qpl_active_flow_ids=431626709"]',  # ← thiếu ở lần trước!
        }

        headers = {
            **self.headers,
            "content-type":           "application/x-www-form-urlencoded",
            "x-fb-lsd":               self.lsd,
            "x-fb-friendly-name":     "ComposerStoryCreateMutation",
            "x-asbd-id":              "359341",
            "referer":                f"https://www.facebook.com/profile.php?id={page_id}&sk=reviews",
        }

        try:
            response = requests.post(
                "https://www.facebook.com/api/graphql/",
                headers=headers,
                data=data,
                proxies=self.proxies,
                timeout=15
            )
        except Exception:
            return False

        if not response.text or '"errors"' not in response.text:
            return True

        try:
            resp_json = response.json()
            for err in resp_json.get("errors", []):
                if err.get("severity") == "CRITICAL":
                    # print(f"   ⚠️ Lỗi rate_page: {err.get('description', err.get('message', ''))}")
                    return False
        except Exception:
            pass
        return False

    # ──────────────────────────────────────────────────────────────
    # BÌNH LUẬN BÀI VIẾT (COMMENT)
    # ──────────────────────────────────────────────────────────────

    def comment(self, post_id: str, text: str) -> bool:
        """
        Đăng bình luận (comment) vào một bài viết.

        Endpoint nội bộ: POST /api/graphql/ (useCometUFICreateCommentMutation)

        Args:
            post_id: ID bài viết (phần số thuần).
                     Ví dụ: "122173519772766399"
                     Nếu dạng "user_post", tự động tách phần post.
            text:    Nội dung bình luận muốn đăng.
                     Ví dụ: "Hay quá!"

        Returns:
            True nếu comment thành công (có comment ID trong response).
            False nếu thất bại.

        Cập nhật 2026-02-20: doc_id và variables lấy từ request thật.
        """
        import json as _json

        if "_" in post_id:
            post_id = post_id.split("_")[1]

        # feedback_id = base64 của "feedback:{post_id}"
        feedback_id = encode_base64(f"feedback:{post_id}")

        variables = {
            "feedLocation":   "DEDICATED_COMMENTING_SURFACE",
            "feedbackSource": 110,
            "groupID":        None,
            "input": {
                "client_mutation_id":  str(uuid.uuid4())[:8],
                "actor_id":            self.actor_id,
                "attachments":         None,
                "feedback_id":         feedback_id,
                "formatting_style":    None,
                "message":             {"ranges": [], "text": text},
                "attribution_id_v2":   (
                    f"ProfileCometTimelineListViewRoot.react,"
                    f"comet.profile.timeline.list,tap_bookmark,"
                    f"1771592438997,271712,{self.actor_id},,"
                ),
                "vod_video_timestamp": None,
                "feedback_referrer":   "/",
                "is_tracking_encrypted": True,
                "tracking":            [],
                "feedback_source":     "DEDICATED_COMMENTING_SURFACE",
                "idempotence_token":   f"client:{uuid.uuid4()}",
                "session_id":          str(uuid.uuid4()),
            },
            "inviteShortLinkKey": None,
            "renderLocation":     None,
            "scale":              1,
            "useDefaultActor":    False,
            "focusCommentID":     None,
            # Relay provider flags từ request thật
            "__relay_internal__pv__groups_comet_use_glvrelayprovider":                        False,
            "__relay_internal__pv__CometUFICommentActionLinksRewriteEnabledrelayprovider":    False,
            "__relay_internal__pv__CometUFICommentAvatarStickerAnimatedImagerelayprovider":   False,
            "__relay_internal__pv__IsWorkUserrelayprovider":                                  False,
        }

        data = {
            "av":                          self.actor_id,
            "__user":                      self.actor_id,
            "__a":                         "1",
            "__hs":                        "20504.HCSV2:comet_pkg.2.1...0",
            "dpr":                         "1",
            "__ccg":                       "GOOD",
            "__rev":                       "1033775652",
            "fb_dtsg":                     self.fb_dtsg,
            "jazoest":                     self.jazoest,
            "lsd":                         self.lsd,
            "fb_api_caller_class":         "RelayModern",
            "fb_api_req_friendly_name":    "useCometUFICreateCommentMutation",
            "variables":                   _json.dumps(variables),
            "server_timestamps":           "true",
            "doc_id":                      "33964973576450400",   # ✅ Lấy từ request thật 2026-02-20
        }

        headers = {
            **self.headers,
            "content-type":       "application/x-www-form-urlencoded",
            "x-fb-lsd":           self.lsd,
            "x-fb-friendly-name": "useCometUFICreateCommentMutation",
            "x-asbd-id":          "359341",
            "referer":            f"https://www.facebook.com/profile.php?id={self.actor_id}",
        }

        try:
            response = requests.post(
                "https://www.facebook.com/api/graphql/",
                headers=headers,
                data=data,
                proxies=self.proxies,
                timeout=15
            )
        except Exception:
            return False

        if '"comment_create"' in response.text and '"feedback"' in response.text:
            return True
        if not response.text or '"errors"' not in response.text:
            return True

        try:
            resp_json = response.json()
            critical = [e for e in resp_json.get("errors", []) if e.get("severity") == "CRITICAL"]
            if critical:
                # print(f"   ⚠️ Lỗi comment: {critical[0].get('description', critical[0].get('message', ''))}")
                return False
            elif not resp_json.get("errors"):
                return True
        except Exception:
            pass
        return False

    # ──────────────────────────────────────────────────────────────
    # LIKE / FOLLOW TRANG (LIKE PAGE)
    # ──────────────────────────────────────────────────────────────

    def like_page(self, page_id: str) -> bool:
        """
        Like và Follow một Facebook Page.

        Endpoint nội bộ: POST /api/graphql/ (CometProfilePlusLikeMutation)

        Args:
            page_id: ID số của trang.
                     Tìm trong URL trang: facebook.com/profile.php?id=**180375029024062**
                     Hoặc URL như: facebook.com/pages/.../323713887631229

        Returns:
            True nếu đã like/follow thành công.

        Cập nhật 2026-02-20: doc_id lấy từ request thật.
        """
        import json as _json

        variables = {
            "input": {
                "is_tracking_encrypted": False,
                "page_id": page_id,
                "source": None,
                "tracking": None,
                "actor_id": self.actor_id,
                "client_mutation_id": "1"
            },
            "scale": 1
        }

        data = {
            "av":                          self.actor_id,
            "__user":                      self.actor_id,
            "__a":                         "1",
            "__hs":                        "20504.HCSV2:comet_pkg.2.1...0",
            "dpr":                         "1",
            "__ccg":                       "EXCELLENT",
            "__rev":                       "1033775652",
            "fb_dtsg":                     self.fb_dtsg,
            "jazoest":                     self.jazoest,
            "lsd":                         self.lsd,
            "fb_api_caller_class":         "RelayModern",
            "fb_api_req_friendly_name":    "CometProfilePlusLikeMutation",
            "variables":                   _json.dumps(variables),
            "server_timestamps":           "true",
            "doc_id":                      "25463905889878308",   # ⚠️ Cập nhật 2026-02-20
        }

        headers = {
            **self.headers,
            "content-type":       "application/x-www-form-urlencoded",
            "x-fb-lsd":           self.lsd,
            "x-fb-friendly-name": "CometProfilePlusLikeMutation",
            "x-asbd-id":          "359341",
            "referer":            f"https://www.facebook.com/profile.php?id={page_id}",
        }

        try:
            response = requests.post(
                "https://www.facebook.com/api/graphql/",
                headers=headers,
                data=data,
                proxies=self.proxies,
                timeout=15
            )
        except Exception:
            return False

        if '"IS_SUBSCRIBED"' in response.text or '"subscribe_status"' in response.text:
            return True
        try:
            err = _json.loads(response.text)
            critical = [e for e in err.get("errors", []) if e.get("severity") == "CRITICAL"]
            if critical:
                return False
                # print(f"   ⚠️ Like page lỗi: {critical[0].get('description', critical[0].get('message'))}")
            elif not err.get("errors"):
                return True
        except Exception:
            pass
        return False

    # ──────────────────────────────────────────────────────────────
    # THAM GIA NHÓM (JOIN GROUP)
    # ──────────────────────────────────────────────────────────────

    def join_page(self, group_id: str) -> bool:
        """
        Tham gia vào một Facebook Group.

        Endpoint nội bộ: POST /api/graphql/ (GroupCometJoinForumMutation)

        Args:
            group_id: ID số của nhóm (lấy từ URL nhóm).

        Returns:
            True nếu yêu cầu tham gia được gửi thành công.
            (Với nhóm public: tham gia ngay. Với nhóm private: chờ duyệt.)
        """
        data = {
            "av":                          self.actor_id,
            "__user":                      self.actor_id,
            "__a":                         "1",
            "__hs":                        "19363.HYP:comet_pkg.2.1.0.2.1",
            "dpr":                         "2",
            "__ccg":                       "EXCELLENT",
            "__rev":                       "1006794317",
            "fb_dtsg":                     self.fb_dtsg,
            "jazoest":                     self.jazoest,
            "lsd":                         self.lsd,
            "fb_api_caller_class":         "RelayModern",
            "fb_api_req_friendly_name":    "GroupCometJoinForumMutation",
            "variables": (
                f'{{"feedType":"DISCUSSION",'
                f'"groupID":"{group_id}",'
                f'"imageMediaType":"image/x-auto",'
                f'"input":{{'
                f'"action_source":"GROUP_MALL",'
                f'"attribution_id_v2":"CometGroupDiscussionRoot.react,'
                f'comet.group,via_cold_start,1673041528761,114928,2361831622,",'
                f'"group_id":"{group_id}",'
                f'"group_share_tracking_params":{{'
                f'"app_id":"2220391788200892",'
                f'"exp_id":"null",'
                f'"is_from_share":false}},'
                f'"actor_id":"{self.actor_id}",'
                f'"client_mutation_id":"1"}},'
                f'"inviteShortLinkKey":null,'
                f'"isChainingRecommendationUnit":false,'
                f'"isEntityMenu":true,'
                f'"scale":2,'
                f'"source":"GROUP_MALL",'
                f'"renderLocation":"group_mall",'
                f'"__relay_internal__pv__GroupsCometEntityMenuEmbeddedrelayprovider":true,'
                f'"__relay_internal__pv__GlobalPanelEnabledrelayprovider":false}}'
            ),
            "server_timestamps": "true",
            "doc_id":            "5853134681430324",
            "fb_api_analytics_tags": '[\"qpl_active_flow_ids=431626709\"]',
        }

        try:
            response = requests.post(
                "https://www.facebook.com/api/graphql/",
                headers=self.headers,
                data=data,
                proxies=self.proxies,
                timeout=15
            )
        except Exception:
            return False

        if self.actor_id in response.text:
            return True
        return False

    # ──────────────────────────────────────────────────────────────
    # THEO DÕI NGƯỜI DÙNG (FOLLOW USER)
    # ──────────────────────────────────────────────────────────────

    def follow(self, user_id: str) -> bool:
        """
        Theo dõi (Follow/Subscribe) một người dùng Facebook.

        Endpoint nội bộ: POST /api/graphql/ (CometUserFollowMutation)

        Args:
            user_id: UID số của người dùng muốn theo dõi.

        Returns:
            True nếu đã follow thành công.
        """
        data = {
            "av":                          self.actor_id,
            "__user":                      self.actor_id,
            "__a":                         "1",
            "__hs":                        "19904.HYP:comet_pkg.2.1..2.1",
            "dpr":                         "1",
            "__ccg":                       "GOOD",
            "__rev":                       "1014584891",
            "fb_dtsg":                     self.fb_dtsg,
            "jazoest":                     self.jazoest,
            "lsd":                         self.lsd,
            "fb_api_caller_class":         "RelayModern",
            "fb_api_req_friendly_name":    "CometUserFollowMutation",
            "variables": (
                f'{{"input":{{'
                f'"attribution_id_v2":"ProfileCometTimelineListViewRoot.react,'
                f'comet.profile.timeline.list,unexpected,1719765181042,489343,250100865708545,,",'
                f'"is_tracking_encrypted":false,'
                f'"subscribe_location":"PROFILE",'
                f'"subscribee_id":"{user_id}",'
                f'"tracking":null,'
                f'"actor_id":"{self.actor_id}",'
                f'"client_mutation_id":"5"}},'
                f'"scale":1}}'
            ),
            "server_timestamps": "true",
            "doc_id":            "25581663504782089",
        }

        try:
            response = requests.post(
                "https://www.facebook.com/api/graphql/",
                headers=self.headers,
                data=data,
                proxies=self.proxies,
                timeout=15
            )
        except Exception:
            return False

        if '"subscribe_status":"IS_SUBSCRIBED"' in response.text:
            return True
        return False

