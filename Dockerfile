FROM amazon/aws-lambda-python:3.12

RUN dnf install -y atk cups-libs gtk3 libXcomposite alsa-lib \
  libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
  libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
  xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm unzip


ENV CHROME_DOWNLOAD_PATH="/opt/chrome-linux.zip"
ENV DRIVER_DOWNLOAD_PATH="/opt/chrome-driver-linux.zip"
ENV CHROME_VERSION="131.0.6778.85"

RUN curl -Lo $DRIVER_DOWNLOAD_PATH "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip" && \
  curl -Lo $CHROME_DOWNLOAD_PATH "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chrome-linux64.zip" && \
  unzip $DRIVER_DOWNLOAD_PATH -d /opt && \
  unzip $CHROME_DOWNLOAD_PATH -d /opt && \
  rm $DRIVER_DOWNLOAD_PATH $CHROME_DOWNLOAD_PATH

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

COPY ./src/ ${LAMBDA_TASK_ROOT}

CMD [ "marathon_gear.handler" ]
