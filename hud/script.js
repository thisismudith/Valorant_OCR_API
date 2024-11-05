const URL = "127.0.0.1:8000", loc = "C:/Users/dagam/Codes/Valorant_OCR_API/images/img1.png";
let socket = new WebSocket(`ws://${URL}/update-during-round`),
firtTime = true;

function mapPlayer(pos, player, firstTime=false){
  const maxUltPoints = player.ult[1],
  relPos = (pos % 5 == 0) ? 5 : pos % 5,
  teamA = document.querySelector(".teamA"),
  teamB = document.querySelector(".teamB");

  if(player.team == "A"){
    playerTeam = teamA;
    oppTeam = teamB;
  }else{
    playerTeam = teamB;
    oppTeam = teamA;
  }

  const playerHUD = playerTeam.querySelector(`#p${relPos}`);


  // Only check sides and teams for 1st player of both teams
  if (pos % 5 == 1){
    if (player.side == "attack"){
      color = "green";
      playerTeam.id = "attackers";
      oppTeam.id = "defenders";
    }else{
      color = "red";
      playerTeam.id = "defenders";
      oppTeam.id = "attackers";
    }
  }

  // Update player name and agents (if first time)
  if (firstTime){
    playerHUD.querySelector("#name").textContent = player.name;
    playerHUD.querySelector("#agent img").src = `../assets/agents/${player.agent}.png`;
    playerHUD.querySelector(".ult-icon img").src = `../assets/ults/${player.agent}.png`;
    if (maxUltPoints > 6){
      for (let i = 7; i <= maxUltPoints; i++){
        playerHUD.querySelector(".ult").insertAdjacentHTML("beforeend", `<div id="ult-${i}" class="ult-point"></div>`);
      }
    }
  }

  // Update creds
  playerHUD.querySelectorAll(".creds").forEach(cred => {cred.textContent = player.creds.toLocaleString()});

  // If player dead, we don't need to update other things
  if (player.weapon == "dead"){
    playerHUD.classList.add("dead");
    return;
  }else{
    playerHUD.classList.remove("dead");
    playerHUD.querySelector("#weapon img").src = `../assets/guns/${player.weapon}.png`;
  }

  // Shield
  if (player.shield == "none"){
    playerHUD.querySelector(".shield").src = `../assets/web/${color}_heavy.png`;
    playerHUD.querySelector(".shield").style.opacity = 0;
  }else{
    playerHUD.querySelector(".shield").src = `../assets/web/${color}_${player.shield}.png`;
  }


  // KDA
  playerHUD.querySelector("#kills").textContent = player.kda[0];
  playerHUD.querySelector("#deaths").textContent = player.kda[1];
  playerHUD.querySelector("#assists").textContent = player.kda[2];


  // Ult
  if (player.ult[0] == maxUltPoints){
    playerHUD.querySelector(".ult").classList.add("ready");
    for (let i = 1; i <= maxUltPoints; i++){
      playerHUD.querySelector(".ult").querySelectorAll("div:not(.ult-icon)").forEach(point => point.classList.remove("fill"));
    }
  }else{
    playerHUD.querySelector(".ult").classList.remove("ready");
    for (let i = 1; i <= player.ult[0]; i++){
      playerHUD.querySelector(`#ult-${i}`).classList.add("fill");
    }
    for (let i = player.ult[0]+1; i <= maxUltPoints; i++){
      playerHUD.querySelector(`#ult-${i}`).classList.remove("fill");
    }
  }
}


// Listen for message
socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log("Updated!");
  data.forEach((player, i) => {
      mapPlayer(i+1, player, player["firstTime"]);
  });
};

function connect(socket){
  socket.onopen = function(e) {
    socket.send("start");
  };

  // Listen for message
  socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log("Updated!");
    data.forEach((player, i) => {
        mapPlayer(i+1, player, player["firstTime"]);
    });
  };

  // Handle WebSocket errors
  socket.onerror = function(error) {
    console.error("WebSocket error:", error);
  };
}

// Start receiving updates
function startUpdates() {
  if (socket.readyState == 3) socket = new WebSocket(`ws://${URL}/update-during-round`);
  else socket.send("start");
  connect(socket);
}

// Stop receiving updates
function stopUpdates() {
  socket.send("stop");
  socket.close();
  console.log("Stopping!")
}

// POST request for update snapshot
function updateSnapshot(){
    fetch(`http://127.0.0.1:8000/update-snapshot?loc=${loc}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      // body: JSON.stringify(data)  // Make sure the body is a JSON string
    })
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error("Error:", error));
}