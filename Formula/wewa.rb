class Wewa < Formula
  desc "Display web content as desktop wallpaper"
  homepage "https://github.com/ownself/wewa"
  version "0.3.0"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/ownself/wewa/releases/download/v0.3.0/wewa-macos-arm64.tar.gz"
      sha256 "76a833c2ff67b343202738f8b97a8fb7189b505e3d5a84ee898f2f71097228f9"
    else
      url "https://github.com/ownself/wewa/releases/download/v0.3.0/wewa-macos-x64.tar.gz"
      sha256 "f0adedb2821c58754b049e137ceeebd14f1ec45601fccd8d417e1be97a2fba20"
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
