echo "Executing create_dependency_zip.sh"

pip install -r $PATH_MODULE/../requirements.txt --target $PYTHON_DEPENDENCIES_PATH

mkdir -p $CHROMIUM_DEPENDENCIES_PATH
curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > $CHROMIUM_DEPENDENCIES_PATH/chromedriver.zip
unzip $CHROMIUM_DEPENDENCIES_PATH/chromedriver.zip -d $CHROMIUM_DEPENDENCIES_PATH
rm $CHROMIUM_DEPENDENCIES_PATH/chromedriver.zip

curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-41/stable-headless-chromium-amazonlinux-2017-03.zip > $CHROMIUM_DEPENDENCIES_PATH/headless-chromium.zip
unzip $CHROMIUM_DEPENDENCIES_PATH/headless-chromium.zip -d $CHROMIUM_DEPENDENCIES_PATH
rm $CHROMIUM_DEPENDENCIES_PATH/headless-chromium.zip
