cask "prisma-access-browser-linux" do
  version "157.19.6.79"
  sha256 "ba92f103a44162bcd57b885be56b75c806655fd09d9de70b707ac05d121d9b76"

  url "https://updates.talon-sec.com/releases/Prisma%20Access%20Browser/linux_rpm/stable/x64/prisma-access-browser-stable-157-157.19.6.79-999c7e0c.19.6.79-1.x86_64.rpm"

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

  artifact "prisma-access-browser.desktop",
           target: "#{Dir.home}/.local/share/applications/prisma-access-browser.desktop"

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

    mkdir_p ".local/share/applications", base: :home

    if_path_exists "prisma-extracted/usr/share/applications/prisma-access-browser.desktop" do
      run "/bin/sed",
          args: [
            "-e",
            "s|^Exec=/usr/bin/prisma-access-browser-stable %U|Exec={{HOMEBREW_PREFIX}}/bin/prisma-access-browser %U|",
            "-e",
            "s|^Exec=/usr/bin/prisma-access-browser-stable$|Exec={{HOMEBREW_PREFIX}}/bin/prisma-access-browser|",
            "-e",
            "s|^Exec=/usr/bin/prisma-access-browser-stable --incognito$|Exec={{HOMEBREW_PREFIX}}/bin/prisma-access-browser --incognito|",
            "-e",
            "s|^Icon=.*|Icon={{staged_path}}/prisma-extracted/opt/paloaltonetworks/pab/product_logo_256.png|",
            "{{staged_path}}/prisma-extracted/usr/share/applications/prisma-access-browser.desktop"
          ],
          stdout_path: "prisma-access-browser.desktop"
    end

    remove [
      "prisma.rpm",
      "prisma.cpio"
    ]
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