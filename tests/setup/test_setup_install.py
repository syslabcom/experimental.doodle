from experimental.doodle import PACKAGE_NAME


class TestSetupInstall:
    def test_addon_installed(self, installer):
        """Test if experimental.doodle is installed."""
        assert installer.is_product_installed(PACKAGE_NAME) is True

    def test_browserlayer(self, browser_layers):
        """Test that IBrowserLayer is registered."""
        from experimental.doodle.interfaces import IBrowserLayer

        assert IBrowserLayer in browser_layers

    def test_latest_version(self, profile_last_version):
        """Test latest version of default profile."""
        assert profile_last_version(f"{PACKAGE_NAME}:default") == "1000"

    def test_folder_type_installed(self, portal):
        """Test folder content type is registered."""
        assert "experimental.doodle.folder" in portal.portal_types

    def test_folder_type_add_permission(self, portal):
        """Test folder content type uses custom add permission."""
        fti = portal.portal_types["experimental.doodle.folder"]
        assert fti.add_permission == "experimental.doodle.AddDoodleFolder"

    def test_date_type_installed(self, portal):
        """Test date content type is registered."""
        assert "experimental.doodle.date" in portal.portal_types

    def test_date_type_add_permission(self, portal):
        """Test date content type uses custom add permission."""
        fti = portal.portal_types["experimental.doodle.date"]
        assert fti.add_permission == "experimental.doodle.AddDoodleDate"

    def test_folder_allows_only_date_type(self, portal):
        """Test folder is configured to accept only date items."""
        fti = portal.portal_types["experimental.doodle.folder"]
        assert fti.filter_content_types is True
        assert fti.allowed_content_types == ("experimental.doodle.date",)

    def test_folder_default_view_is_doodle(self, portal):
        """Test folder type defaults to the doodle layout."""
        fti = portal.portal_types["experimental.doodle.folder"]
        assert fti.default_view == "doodle"
        assert fti.immediate_view == "doodle"

    def test_date_type_not_global(self, portal):
        """Test date type is not globally addable."""
        fti = portal.portal_types["experimental.doodle.date"]
        assert fti.global_allow is False
