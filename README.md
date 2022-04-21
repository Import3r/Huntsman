# Huntsman - web application recon and asset discovery

![image](https://user-images.githubusercontent.com/60158098/121773424-8c9aaa00-cb84-11eb-855e-ccbf3fb071b5.png)

## Description

A python script that automates my discovery process and recon workflow for given target domains/assets, by utilizing open-source tools used for web application  testing.

## What it does

- Utilizes "Amass" in enum mode to collect subdomains under given domains.
- Utilizes an open-source tool by [gwen001](https://github.com/gwen001) to perform GitHub-dorking with a GitHub access token to collect more subdomains.
- Utilizes "Aquatone" to perform visual sorting of discovered end-points to seperate unique web applications from duplicate ones.
- Utilizes "Subdomainizer" to scan responses and JS files for potentially sensitive information.

## Setup

- Clone "Huntsman" from Github:

```bash
git clone https://github.com/Import3r/Huntsman.git
```

- Change directory to "Huntsman":

```bash
cd Huntsman
```

- Install needed packages from apt_packages.txt:

```bash
xargs -r -a apt_packages.txt sudo apt-get install -y
```

- Run "Huntsman":

```bash
python3 main.py
```

Note: running "Huntsman" for the first time may trigger the installer prompt for missing tools.
