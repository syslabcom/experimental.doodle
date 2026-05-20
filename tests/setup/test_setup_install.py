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
