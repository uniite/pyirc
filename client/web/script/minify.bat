cd ../js
cat kapow.js observable.js | uglifyjs > kapow.min.js
rm kapow.js
