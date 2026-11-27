cask "discord-linux" do
  version "1.0.171"
  sha256 "efc517cf1551d93bdcb6f5c03fec52c2f05eb82805bd0ab2beed671bce56fdc8"

  url "https://dl.discordapp.net/apps/linux/1.0.171/discord-1.0.171.tar.gz"

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
  depends_on arch: :x86_64

  binary "Discord/discord",
         target: "discord"

  artifact "discord.desktop",
           target: "#{Dir.home}/.local/share/applications/discord.desktop"

  preflight_steps do
    mkdir_p ".local/share/applications", base: :home

    write_file "discord.desktop", <<~EOS
      [Desktop Entry]
      Name=Discord
      Comment=All-in-one voice and text chat
      GenericName=Internet Messenger
      Exec={{HOMEBREW_PREFIX}}/bin/discord --url -- %u
      Icon={{staged_path}}/Discord/discord.png
      Type=Application
      StartupNotify=true
      StartupWMClass=discord
      Categories=Network;InstantMessaging;
      MimeType=x-scheme-handler/discord;

      Actions=new-window;

      [Desktop Action new-window]
      Name=Open Discord
      Exec={{HOMEBREW_PREFIX}}/bin/discord
      Icon={{staged_path}}/discord.png
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