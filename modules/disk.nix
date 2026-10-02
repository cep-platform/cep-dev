{
  disko.devices = {
    disk = {
      main = {
        device = "/dev/sda";
        type = "disk";

        content = {
          type = "gpt";

          partitions = {
            root = {
              size = "100%";

              content = {
                type = "filesystem";
                format = "ext4";
                mountpoint = "/";
              };
            };
          };
        };
      };
    };
  };

  boot.loader.grub = {
    enable = true;
    device = "/dev/sda";
  };
}
