FROM nixos/nix:latest

WORKDIR /opt

# Clone the repository
RUN nix-shell -p git --run "git clone --depth=1 https://github.com/seekers-dev/seekers.git"

WORKDIR /opt/seekers

# Populate the nix store during the image build
RUN nix-shell --run "true"
RUN curl -Lo seekers-api.zip https://github.com/seekers-dev/seekers-api/releases/download/prerelease/seekers-api.zip
RUN nix-shell -p unzip --run "unzip seekers-api.zip"
RUN nix-shell -p netcat-gnu
RUN rm -f config.ini

# Default command
ENTRYPOINT ["nix-shell", "--run"]
CMD ["bash"]
