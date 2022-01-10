// Your web app's Firebase configuration
var firebaseConfig = {
    apiKey: "AIzaSyBwIYopqpPOQmdVMgt4JX76-7Mb9YLpRkc",
    authDomain: "weather-app-a732e.firebaseapp.com",
    databaseURL: "https://weather-app-a732e.firebaseio.com",
    projectId: "weather-app-a732e",
    storageBucket: "weather-app-a732e.appspot.com",
    messagingSenderId: "461429962298",
    appId: "1:461429962298:web:8632fff673f3139391a703",
    measurementId: "G-70Z9VN7LNQ"
  },
  database;
// Initialize Firebase
firebase.initializeApp(firebaseConfig);
firebase.analytics();
database = firebase.database();

function add_query_to_database(query) {
  database.ref("/query/iw/").push(query);
}

function getToday() {
  var today = new Date();
  var dd = String(today.getDate()).padStart(2, '0');
  var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
  var yyyy = today.getFullYear();
  today = mm + '/' + dd + '/' + yyyy;
  return today;
}

function handleXhr() {
  var http = new XMLHttpRequest();
  var queryText = document.querySelector("#input").value
  var url = 'https://interstellarbroadcasting.center/nlp/pythontest.php';
  var params = 'query=' + encodeURIComponent(queryText);
  http.open('POST', url, true);
  http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
  http.onreadystatechange = function() { //Call a function when the state changes.
    if (http.readyState == 4 && http.status == 200) {
      //ggf anpassen, je nach dem wo es angezeigt werden soll
      queryText = document.querySelector("#input").value
      document.querySelector("#answer").innerHTML = http.responseText;
      document.querySelector("#loadingBar").setAttribute("src", "")
      add_query_to_database({
        "time_stemp": [getToday()],
        "query": [queryText],
        "answer": [http.responseText]
      });
    }
  }
  http.send(params);
}

sendButton = document.querySelector("#send_query")
sendButton.addEventListener("click", function() {
  queryText = document.querySelector("#input").value
  document.querySelector("#loadingBar").setAttribute("src", "loading.gif")
  document.querySelector("#answer").innerHTML = "";
  handleXhr();
});
