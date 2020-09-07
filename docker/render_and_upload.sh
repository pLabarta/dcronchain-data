cd ${GITHUB_REPO}
git pull
cd ..
echo "Updating DCR On Chain data..."
mkdir ${GITHUB_REPO}/data
python3 generate_charts.py
python3 generate_insights.py
echo "Uploading new data to Github"
cd ${GITHUB_REPO}/data
git add .
git commit -m "regular data update"
git push https://${GITHUB_TOKEN}:x-oauth-basic@${GITHUB_URL} master

