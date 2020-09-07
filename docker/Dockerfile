FROM debian

# House cleaning
RUN apt-get update --fix-missing
# Install git
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install git
# Install python dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install python3-pip python3-venv
RUN DEBIAN_FRONTEND=noninteractive python3 -m pip install --upgrade pip setuptools wheel
# Set up virtual env
ENV VIRTUAL_ENV=/opt/env
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# Install Python dependencies
ADD requirements.txt .
RUN DEBIAN_FRONTEND=noninteractive pip3 install -r requirements.txt
# Git and Github config
# REPLACE WITH YOUR CONFIG
# Clone Checkonchain
RUN DEBIAN_FRONTEND=noninteractive git clone https://github.com/checkmatey/checkonchain

# Git config
### CONFIG ###
ENV GITHUB_EMAIL="YOUR EMAIL"
ENV GITHUB_USER="YOUR USERNAME"
ENV GITHUB_TOKEN="YOUR TOKEN"
ENV GITHUB_REPO="data"
# Set up git congif
ENV GITHUB_URL="github.com/${GITHUB_USER}/${GITHUB_REPO}.git"
RUN git config --global user.email $GITHUB_EMAIL
RUN git config --global user.name $GITHUB_USER

# Get current data
RUN DEBIAN_FRONTEND=noninteractive git clone https://${GITHUB_URL}

ADD generate_charts.py .
ADD generate_insights.py .
ADD render_and_upload.sh .
RUN chmod 777 render_and_upload.sh
CMD ./render_and_upload.sh

