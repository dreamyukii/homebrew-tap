cask "discord-linux" do
  version "1.0.169"
  sha256 "21b47a62f83dbba99c128a379b6d901075b9eedb5e22a72dae87b7cd08088fa3"

  url "https://dl.discordapp.net/apps/linux/1.0.169/discord-1.0.169.tar.gz"

  name "Discord"
  desc "Voice, video and text communication platform"
  homepage "https://discord.com/"

  livecheck do
    url "https://discord.com/api/updates/stable?platform=linux"

    strategy :json do |json|
      json["name"]
    end
  end

  depends_on :linux

  binary "Discord/Discord",
       target: "discord"

  artifact "discord.desktop",
           target: "#{Dir.home}/.local/share/applications/discord.desktop"
  preflight_steps do
    run "/usr/bin/find",
        args: ["{{staged_path}}"]
  end
  preflight_steps do
    mkdir_p ".local/share/applications", base: :home

    write_file "discord.desktop", <<~EOS
      [Desktop Entry]
      Name=Discord
      StartupWMClass=discord
      Comment=All-in-one voice and text chat for gamers that's free, secure, and works on both your desktop and phone.
      GenericName=Internet Messenger
      Exec={{HOMEBREW_PREFIX}}/bin/discord --url -- %u
      Icon={{staged_path}}/discord.png
      Type=Application
      Categories=Network;InstantMessaging;
      MimeType=x-scheme-handler/discord;
      StartupNotify=true
      Terminal=false
    EOS
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