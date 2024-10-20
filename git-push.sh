if [ -z "$1" ]
  then
    echo "No commit message supplied"
    exit 1
fi
echo "Add ..."
git add .
echo "Commit ..."
git commit -m "$1"
echo "Push ..."
git push origin feature/backend