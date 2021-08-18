# Huntsman - web application recon and asset discovery

![image](https://user-images.githubusercontent.com/60158098/121773424-8c9aaa00-cb84-11eb-855e-ccbf3fb071b5.png)

## Description

A python script that utilizes open-source tools to automate my discovery process and recon flow for given target domains/assets. The tools and techniques included are what I usually use in my workflow when testing websites and looking for assets in a provided scope.

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

- Install needed packages from packages.txt:

```bash
xargs -r -a packages.txt sudo apt-get install
```

- Run "Huntsman":

```bash
python3 Huntsman.py
```

Note: running "Huntsman" for the first time may trigger the installer prompt for missing tools.
