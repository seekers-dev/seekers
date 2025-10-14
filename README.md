<div align=center>
    <h1 align=center>Seekers</h1>
    <!-- Badges -->
    <div>
        <img src="https://github.com/seekers-dev/seekers/actions/workflows/python-app.yml/badge.svg" alt="Python Version 3.9/3.10">
        <img src="https://github.com/seekers-dev/seekers/actions/workflows/github-code-scanning/codeql/badge.svg" alt="CodeQL">
        <img src="https://github.com/seekers-dev/seekers/actions/workflows/python-app.yml/badge.svg" alt="pre-release">
    </div>
    <i>Learn to code with games.</i>
</div>

<div>
    <img alt="Game Preview" align=right width=40% src=https://user-images.githubusercontent.com/37810842/226148194-e5b55d57-ed84-4e71-869b-d062b101b345.png>
    <ul >
        <li>Artificial intelligence programming challenge, hopefully suited for school students.</li>
        <li>AIs compete by controlling bouncy little circles ("seekers") trying to collect the most goals.</li>
        <li>Based on Python 3 and pygame.</li>
    </ul>
</div>

## Getting started

### Setup

You can download prebuild binaries from the latest release [here]() or from the prerelease [here]().

Alternativly, you can build it yourself. You can do this by running the following commands:

```sh
# Clone this project
git clone https://github.com/seekers-dev/seekers.git
cd seekers
# Install all requirements
python -m pip install --upgrade pip
pip install -r requirements.txt
# Download the api headers
curl -Lo seekers-api.zip https://github.com/seekers-dev/seekers-api/releases/download/prerelease/seekers-api.zip
unzip seekers-api.zip
```

### Run seekers

If you want to run the seekers game with the AI files, you should run the following command: 

```sh
python seekers.py [files]
```
