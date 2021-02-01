# Gnome appindicator dns switcher
https://pypi.org/project/gnome-dns-switcher/

## Setup
```shell
# sudo so the script is added to $PATH, you can also install normally and fix $PATH :)
sudo pip3 install gnome-dns-switcher
```

- Create a config.yml, see [Config](#config)

## Running

```shell
gnome-dns-switcher --config /path/to/config.yml
```

## Config

### Sample:

```yaml
servers:
  CloudFlare: 1.1.1.1
  Google DNS:
    - 8.8.8.8
    - 8.8.4.4
  localhost: 127.0.0.1, 127.0.1.1
devices:
  - wlp2s0
```

### Explanation

#### `servers:`

- A list of servers that can be switched between
- Name is just used for displaying
- You can define one or more ips
- On launch, we'll try to detect if the current settings match any of the servers

#### `devices:`

- optional, will display all non-bridge connections otherwise
- one or more devices to show in the switcher
    - List all your devices by running `ip link show` in a terminal

### You possibly need to install these dependencies

```shell
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### Useful links

- https://gjs-docs.gnome.org/
