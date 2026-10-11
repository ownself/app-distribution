class Wewa < Formula
  desc "Display web content as desktop wallpaper"
  homepage "https://github.com/ownself/wewa"
  version "0.4.0"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/ownself/wewa/releases/download/v0.4.0/wewa-macos-arm64.tar.gz"
      sha256 "bb3da022bcbcee03eaf873b9cfb5fd1cae0d0ed155a130ca18ce3f5cecd997e8"
    else
      url "https://github.com/ownself/wewa/releases/download/v0.4.0/wewa-macos-x64.tar.gz"
      sha256 "9d475d46d56b5f598f0d25ec994d54cfceba3f7e17a4bdf6118c54dfe0de10ee"
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
