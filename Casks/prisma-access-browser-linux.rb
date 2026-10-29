cask "prisma-access-browser-linux" do
  version "156.17.8.74"
  sha256 "880a5da75927aefb1b17af8f0e43ff2a6fd1069b57e35ee381c456d11fe6f2dc"

  url "https://updates.talon-sec.com/releases/Prisma%20Access%20Browser/linux_rpm/stable/x64/prisma-access-browser-stable-156-156.17.8.74-6065d61a.17.8.74-1.x86_64.rpm"

  name "Prisma Access Browser"
  desc "Enterprise browser from Palo Alto Networks"
  homepage "https://www.paloaltonetworks.com/"

  livecheck do
    url "https://releases.talon-sec.com/api/v1/appcast.xml?appid=%7Bdfef2477-4f0e-454b-bc0d-03ce61074e4c%7D&platform=linux_rpm&architecture=x64&channel=stable"

    strategy :sparkle do |item|
      item.short_version
    end
  end

  depends_on arch: :x86_64
  depends_on formula: "cpio"
  depends_on formula: "rpm2cpio"
  depends_on :linux

  binary "#{staged_path}/prisma-extracted/opt/paloaltonetworks/pab/prisma-access-browser",
         target: "prisma-access-browser"

  preflight_steps do
    move "prisma-access-browser*.rpm",
         "prisma.rpm",
         source_glob: true

    mkdir_p "prisma-extracted"

    run "{{HOMEBREW_PREFIX}}/opt/rpm2cpio/bin/rpm2cpio",
        args: ["{{staged_path}}/prisma.rpm"],
        stdout_path: "prisma.cpio"

    run "{{HOMEBREW_PREFIX}}/opt/cpio/bin/cpio",
        args: ["-idmv"],
        stdin_path: "prisma.cpio",
        chdir: "prisma-extracted"

    remove ["prisma.rpm", "prisma.cpio"]

    mkdir_p ".local/share/applications", base: :home

    if_path_exists "prisma-extracted/usr/share/applications/prisma-access-browser.desktop" do
      run "/bin/sed",
          args: [
            "-e",
            "s|^Exec=.*|Exec={{HOMEBREW_PREFIX}}/bin/prisma-access-browser %U|",
            "{{staged_path}}/prisma-extracted/usr/share/applications/prisma-access-browser.desktop"
          ],
          stdout_path: "prisma-access-browser.desktop"

      copy "prisma-access-browser.desktop",
           ".local/share/applications/prisma-access-browser.desktop",
           target_base: :home
    end

    unless_path_exists "prisma-extracted/usr/share/applications/prisma-access-browser.desktop" do
      write_file ".local/share/applications/prisma-access-browser.desktop", <<~EOS, base: :home
        [Desktop Entry]
        Name=Prisma Access Browser
        Comment=Enterprise Browser
        Exec={{HOMEBREW_PREFIX}}/bin/prisma-access-browser %U
        Icon=prisma-access-browser
        Type=Application
        Categories=Network;WebBrowser;
      EOS
    end
  end

  uninstall_postflight_steps do
    remove ".local/share/applications/prisma-access-browser.desktop",
           base: :home
  end

  zap trash: [
    "~/.cache/Prisma Access Browser",
    "~/.config/Prisma Access Browser",
    "~/.pab",
  ]
end