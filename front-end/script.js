// Init Firebase configurations
var firebaseConfig = {
    apiKey: "AIzaSyBwIYopqpPOQmdVMgt4JX76-7Mb9YLpRkc",
    authDomain: "weather-app-a732e.firebaseapp.com",
    databaseURL: "https://weather-app-a732e.firebaseio.com",
    projectId: "weather-app-a732e",
    storageBucket: "weather-app-a732e.appspot.com",
    messagingSenderId: "461429962298",
    appId: "1:461429962298:web:8632fff673f3139391a703",
    measurementId: "G-70Z9VN7LNQ",
  },
  database;
// Initialize Firebase
firebase.initializeApp(firebaseConfig);
database = firebase.database();

var userId;

function add_query_to_database(query) {
  database.ref("/query/final/").push(query);
}

function getToday() {
  var today = new Date();
  var d = String(today.getDate()).padStart(2, "0");
  var m = String(today.getMonth() + 1).padStart(2, "0"); //January is 0!
  var y = today.getFullYear();
  var h = today.getHours();
  var min = today.getMinutes();
  today =
    y +
    "." +
    ("00" + m).slice(-2) +
    "." +
    ("00" + d).slice(-2) +
    " " +
    ("00" + h).slice(-2) +
    ":" +
    ("00" + min).slice(-2);
  return today;
}

function initPopup() {
  let closePopupButton = document.querySelector(".close-img");
  let popup = document.querySelector(".information");
  closePopupButton.addEventListener("click", function () {
    popup.remove();
  });
}

function createUserId(min, max) {
  // min and max included
  userId = Math.floor(Math.random() * (max - min + 1) + min);
}

function addUserMessage(message) {
  let chatElement = document.querySelector(".chat");
  let userMessageElement = document.createElement("div");
  userMessageElement.setAttribute("class", "user-message");
  let textMessageElement = document.createElement("h3");
  let usernameElement = document.createElement("p");
  chatElement.append(userMessageElement);
  userMessageElement.append(textMessageElement);
  userMessageElement.append(usernameElement);
  usernameElement.innerHTML = "User-" + userId;
  textMessageElement.innerHTML = message;
  window.scrollTo(0, document.body.scrollHeight);
}

function addSystemMessage(message) {
  message_edited = message
    .replace(/\.(?![0-9]+)/g, ". ")
    .replace(/\!(?![0-9]+)/g, "! ")
    .replace("\u001b[95m", "")
    .replace("[0m", "");
  let chatElement = document.querySelector(".chat");
  let systemMessageElement = document.createElement("div");
  systemMessageElement.setAttribute("class", "system-response");
  let textMessageElement = document.createElement("h3");
  let systemElement = document.createElement("p");
  chatElement.append(systemMessageElement);
  systemMessageElement.append(textMessageElement);
  systemMessageElement.append(systemElement);
  systemElement.innerHTML = "System";
  textMessageElement.innerHTML = message_edited;
  window.scrollTo(0, document.body.scrollHeight);
}

function addLoadingBar() {
  let loadingBar = document.createElement("div");
  loadingBar.setAttribute("class", "lds-ellipsis");
  loadingBar.innerHTML = "<div></div><div></div><div></div><div></div>";
  let chatElement = document.querySelector(".chat");
  chatElement.append(loadingBar);
  document.querySelector("#input").setAttribute("readonly", "readonly");
  sendButton.disabled = true;
}

function deleteLoadingBar() {
  let loadingBar = document.querySelector(".lds-ellipsis");
  loadingBar.remove();
  document.querySelector("#input").removeAttribute("readonly");
  sendButton.disabled = false;
}

function handleKeyEnter(e) {
  if (e.keyCode === 13) {
    e.preventDefault(); // Ensure it is only this code that rusn
    queryToServer();
  }
}

initPopup();
createUserId(0, 1000000);

function handleXhr(queryText) {
  var http = new XMLHttpRequest();
  var url = "http://127.0.0.1:5000/";
  let formData = new FormData();
  formData.append("query", queryText);

  fetch(url, {
    body: formData,
    method: "post",
  })
    .then((response) => response.text())
    .then((response) => {
      console.log("response: ", response);
      addSystemMessage(response);
      deleteLoadingBar();
      add_query_to_database({
        "time_stamp": [getToday()],
        "query": [queryText],
        "userId": [userId],
        "answer": [response]
      });
    });
  /*
  http.open('POST', url, true);
  http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
  http.onreadystatechange = function() { //Call a function when the state changes.
    if (http.readyState == 4 && http.status == 200) {
      addSystemMessage(http.responseText);
      deleteLoadingBar();
      //document.querySelector("#loadingBar").setAttribute("src", "")
      add_query_to_database({
        "time_stamp": [getToday()],
        "query": [queryText],
        "userId": [userId],
        "answer": [http.responseText]
      });
    }
  }
  http.send(params); */
}

function queryToServer() {
  console.log("Query -> Server");
  queryText = document.querySelector("#input").value;
  addUserMessage(queryText);
  document.querySelector("#input").value = "";
  addLoadingBar();
  //document.querySelector("#loadingBar").setAttribute("src", "loading.gif")
  handleXhr(queryText);
}

sendButton = document.querySelector("#send_query");
sendButton.addEventListener("click", function () {
  queryToServer();
});
