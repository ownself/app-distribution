class Wewa < Formula
  desc "Display web content as desktop wallpaper"
  homepage "https://github.com/ownself/wewa"
  version "0.4.1"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/ownself/wewa/releases/download/v0.4.1/wewa-macos-arm64.tar.gz"
      sha256 "3fd104be1b5bf2e077f860a1b14352fe5c95c8d65ae623ee22e6c08e3de0093b"
    else
      url "https://github.com/ownself/wewa/releases/download/v0.4.1/wewa-macos-x64.tar.gz"
      sha256 "0bac62de343f6ea8266d72a08c7f2bdb3b4149a66ebfa52bf9cc2486352459b6"
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
