cask "discord-linux" do
  arch intel: "x86_64"
  os linux: "linux"

  version "1.0.171"
  sha256 "5d0c79c8b3ad8f84e871e8bf0ef60b4500787f6866fbfeb86c978eee425273b5"

  url "https://stable.dl2.discordapp.net/distro/app/stable/linux/x64/1.0.171/Discord.rpm"

  name "Discord"
  desc "Voice, video and text communication platform"
  homepage "https://discord.com/"

  livecheck do
    url "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=#{os}&arch=x64&format=rpm"

    strategy :header_match do |headers|
      match = headers["location"]&.match(%r{/linux/x64/([^/]+)/Discord\.rpm})
      match[1] if match
    end
  end

  depends_on arch: :x86_64
  depends_on formula: "cpio"
  depends_on formula: "rpm2cpio"
  depends_on :linux

  binary "#{staged_path}/discord",
         target: "discord"

  artifact "discord.desktop",
           target: "#{Dir.home}/.local/share/applications/discord.desktop"

  preflight_steps do
    move "Discord.rpm",
         "discord.rpm"

    mkdir_p "discord-extracted"

    run "{{HOMEBREW_PREFIX}}/opt/rpm2cpio/bin/rpm2cpio",
        args: ["{{staged_path}}/discord.rpm"],
        stdout_path: "discord.cpio"

    run "{{HOMEBREW_PREFIX}}/opt/cpio/bin/cpio",
        args: ["-idmv"],
        stdin_path: "discord.cpio",
        chdir: "discord-extracted"

    mkdir_p ".local/share/applications", base: :home

    run "/bin/sed",
        args: [
          "-e",
          "s|^    bootstrap=/usr/share/.*|    bootstrap={{staged_path}}/discord-extracted/usr/share/discord/updater_bootstrap|",
          "{{staged_path}}/discord-extracted/usr/bin/discord"
        ],
        stdout_path: "discord"

    run "/bin/chmod",
        args: ["+x", "{{staged_path}}/discord"]

    run "/bin/sed",
        args: [
          "-e",
          "s|^Icon=.*|Icon={{staged_path}}/discord-extracted/usr/share/icons/hicolor/256x256/apps/discord.png|",
          "-e",
          "s|^Exec=/usr/bin/discord --url -- %u|Exec={{HOMEBREW_PREFIX}}/bin/discord --url -- %u|",
          "-e",
          "/^Path=/d",
          "{{staged_path}}/discord-extracted/usr/share/applications/discord.desktop"
        ],
        stdout_path: "discord.desktop"

    remove [
      "discord.rpm",
      "discord.cpio"
    ]
  end

  uninstall_postflight_steps do
    remove ".local/share/applications/discord.desktop",
           base: :home
  end

  zap trash: [
    "~/.config/discord",
    "~/.cache/discord",
    "~/.local/share/discord",
  ]
end
