class AiUsageMonitor < Formula
  include Language::Python::Virtualenv

  desc "Monitor AI coding assistant usage with real-time dashboards"
  homepage "https://github.com/aecs4u/ai-usage-monitor"
  url "https://files.pythonhosted.org/packages/source/a/ai-usage-monitor/ai-usage-monitor-4.1.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"  # Update after release
  license "MIT"

  depends_on "python@3.12"

  # Core dependencies
  resource "click" do
    url "https://files.pythonhosted.org/packages/source/c/click/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.7.0.tar.gz"
    sha256 "5cb5123b5cf9ee70584244246816e9114227e0b98ad9176eede6ad54bf5403fa"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/source/p/pydantic/pydantic-2.5.3.tar.gz"
    sha256 "b3ef57c62535b0941697cce638c08900d87fcb67e29cfa99e8a68f747f393f7a"
  end

  resource "pydantic-settings" do
    url "https://files.pythonhosted.org/packages/source/p/pydantic-settings/pydantic_settings-2.1.0.tar.gz"
    sha256 "26b1492e0a24755626ac5e6d715e9077ab7ad4fb5f19a8b7ed7011d52f36141c"
  end

  resource "pytz" do
    url "https://files.pythonhosted.org/packages/source/p/pytz/pytz-2023.3.post1.tar.gz"
    sha256 "7b4fddbeb94a1eba4b557da24f19fdf9db575192544270a9101d8509f9f43d7b"
  end

  resource "toml" do
    url "https://files.pythonhosted.org/packages/source/t/toml/toml-0.10.2.tar.gz"
    sha256 "b3bda1d108d5dd99f4a20d24d9c348e91c4db7ab1b749200bded2f839ccbe68f"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    # Test that the CLI runs
    assert_match "AI Usage Monitor", shell_output("#{bin}/ai-usage-monitor --help")

    # Test version
    assert_match version.to_s, shell_output("#{bin}/ai-usage-monitor --version")

    # Test that it can show help for different views
    system bin/"ai-usage-monitor", "--help"
  end
end
