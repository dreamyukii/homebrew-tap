cask "discord-linux" do
  version "1.0.169"
  sha256 "21b47a62f83dbba99c128a379b6d901075b9eedb5e22a72dae87b7cd08088fa3"

  url "https://dl.discordapp.net/apps/linux/1.0.169/discord-1.0.169.tar.gz"

  name "Discord"
  desc "Voice, video and text communication platform"
  homepage "https://discord.com/"

  livecheck do
    url "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=linux&arch=x64&format=tar.gz"

    strategy :header_match do |headers|
      match = headers["location"]&.match(%r{/apps/linux/([^/]+)/})
      match[1] if match
    end
  end

  depends_on arch: :x86_64
  depends_on :linux

  binary "discord",
         target: "discord"

  artifact "discord.desktop",
           target: "#{Dir.home}/.local/share/applications/discord.desktop"

  preflight_steps do
    mkdir_p ".local/share/applications", base: :home

    run "/bin/sed",
        args: [
          "-e",
          "s|^Exec=.*|Exec={{HOMEBREW_PREFIX}}/bin/discord --url -- %u|",
          "-e",
          "s|^Path=.*|Path={{HOMEBREW_PREFIX}}/bin|",
          "-e",
          "s|^Icon=.*|Icon={{staged_path}}/discord.png|",
          "{{staged_path}}/discord.desktop"
        ],
        stdout_path: "discord.desktop"
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