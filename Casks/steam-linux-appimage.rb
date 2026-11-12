cask "steam-linux-appimage" do
  version "1.0.0.87-3-2026-11-01-1793536013"
  sha256 "b207839124cbec65a8f9fa8d51e9bce2e4c028475920076263cda6ac60f39e27"

  url "https://github.com/ivan-hc/Steam-appimage/releases/download/1.0.0.87-3%402026-11-01_1793536013/Steam-1.0.0.87-3-anylinux-x86_64.AppImage"

  name "Steam AppImage"
  desc "Unofficial Steam AppImage built with RunImage"
  homepage "https://github.com/ivan-hc/Steam-appimage"

  livecheck do
    url "https://api.github.com/repos/ivan-hc/Steam-appimage/releases/latest"

    strategy :json do |json|
      tag = json["tag_name"]
      match = tag&.match(/\A(\d+(?:\.\d+)+-\d+)@(\d{4}-\d{2}-\d{2})_(\d+)\z/)
      "#{match[1]}-#{match[2]}-#{match[3]}" if match
    end
  end

  depends_on arch: :x86_64
  depends_on :linux

  binary "#{staged_path}/Steam-#{version.to_s.sub(/-\d{4}-\d{2}-\d{2}-\d+$/, "")}-anylinux-x86_64.AppImage",
         target: "steam"

  preflight_steps do
    run "/bin/chmod",
        args: [
          "+x",
          "{{staged_path}}/Steam-#{version.to_s.sub(/-\d{4}-\d{2}-\d{2}-\d+$/, "")}-anylinux-x86_64.AppImage"
        ]
  end

  postflight_steps do
    mkdir_p ".local/share/applications",
            base: :home

    write_file ".local/share/applications/steam-linux-appimage.desktop",
               "[Desktop Entry]\nName=Steam\nComment=Unofficial Steam AppImage\nExec={{HOMEBREW_PREFIX}}/bin/steam %U\nIcon=steam\nTerminal=false\nType=Application\nCategories=Game;\nStartupWMClass=steam\n",
               base: :home
  end

  uninstall_postflight_steps do
    remove ".local/share/applications/steam-linux-appimage.desktop",
           base: :home
  end
end
