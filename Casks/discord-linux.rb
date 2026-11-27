cask "discord-linux" do
  arch intel: "x64"

  version "1.0.171"
  sha256 "5d0c79c8b3ad8f84e871e8bf0ef60b4500787f6866fbfeb86c978eee425273b5"

  url "https://stable.dl2.discordapp.net/distro/app/stable/linux/x64/1.0.171/Discord.rpm"

  name "Discord"
  desc "Voice, video and text communication platform"
  homepage "https://discord.com/"

  livecheck do
    url "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=linux&arch=x64&format=tar.gz"

    strategy :header_match do |headers|
      match = headers["location"]&.match(%r{/linux/x64/([^/]+)/})
      match[1] if match
    end
  end

  depends_on arch: :x86_64
  depends_on :linux

  binary "#{staged_path}/discord",
         target: "discord"

  artifact "discord.desktop",
           target: "#{Dir.home}/.local/share/applications/discord.desktop"

  preflight do
    run "/bin/ln",
        args: [
          "-sf",
          "{{staged_path}}/Discord/Discord",
          "{{staged_path}}/discord"
        ]

    run "/bin/cp",
        args: [
          "{{staged_path}}/Discord/discord.png",
          "{{staged_path}}/discord.png"
        ]

    run "/bin/cat",
        args: [],
        stdout_path: "discord.desktop",
        input: <<~EOS
          [Desktop Entry]
          Version=1.0
          Type=Application
          Name=Discord
          Comment=Voice, video and text communication platform
          Exec={{HOMEBREW_PREFIX}}/bin/discord --url -- %u
          Icon={{staged_path}}/discord.png
          Terminal=false
          Categories=Network;InstantMessaging;
          StartupWMClass=discord
          MimeType=x-scheme-handler/discord;
        EOS
  end

  uninstall_postflight do
    remove ".local/share/applications/discord.desktop",
           base: :home
  end

  zap trash: [
    "~/.config/discord",
    "~/.cache/discord",
    "~/.local/share/discord",
  ]
end