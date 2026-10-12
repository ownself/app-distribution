class Wewa < Formula
  desc "Display web content as desktop wallpaper"
  homepage "https://github.com/ownself/wewa"
  version "0.4.2"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/ownself/wewa/releases/download/v0.4.2/wewa-macos-arm64.tar.gz"
      sha256 "55ff226a75474c3dd8ab396973293b74d6f3901b0f465e84f101a3f3e70253f3"
    else
      url "https://github.com/ownself/wewa/releases/download/v0.4.2/wewa-macos-x64.tar.gz"
      sha256 "b451e5ce2f860c1553900190a47bcd4239977d82ed509c9b3c0cb6779490fc92"
    end
  end

  def install
    bin.install "wewa"
    doc.install "README.md" if File.exist?("README.md")
  end

  test do
    system "#{bin}/wewa", "--help"
  end
end
