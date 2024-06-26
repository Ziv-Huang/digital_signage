

/**
 * The preload script runs before. It has access to web APIs
 * as well as Electron's renderer process modules and some
 * polyfilled Node.js functions.
 * 
 * https://www.electronjs.org/docs/latest/tutorial/sandbox
 */
window.addEventListener('DOMContentLoaded', () => {
  const replaceText = (selector, text) => {
    const element = document.getElementById(selector)
    if (element) element.innerText = text
  }

  for (const type of ['chrome', 'node', 'electron']) {
    replaceText(`${type}-version`, process.versions[type])
  }
})
//======================================
// const { contextBridge } = require('electron')=
// contextBridge.exposeInMainWorld('versions', {
//   node: () => process.versions.node,
//   chrome: () => process.versions.chrome,
//   electron: () => process.versions.electron,
//   // we can also expose variables, not just functions
// })
//======================================


module.exports = {
  send_video_end
}

const renderer = require('./renderer')
const WebSocket = require('ws')
const ws = new WebSocket('ws://localhost:8551')
let request_data = null
let timer = null;
let count = 0

/////// test /////////
ws.addEventListener('open', async (event) => {
  console.log("connnect to websocket...");
  ws.send("client is connection")
  timer = setInterval(sendHeartBeat, 1000);
});

ws.addEventListener('message', (event) => {
  count+=1
  console.log(event.data)
  try {
    renderer.server_command(JSON.parse(event.data))
  } catch (e) {
    console.log("not JSON");
  }
});


ws.addEventListener('close', (event) => {
  console.log("close websocket...");
  clearInterval(timer);
});

function sendHeartBeat() {
  if(request_data != null){
    ws.send(request_data)
    request_data = null
  }
  // ws.send(JSON.stringify({
  //   type: "HEATBEAT",
  //   data: "SYN",
  // }));
}

function send_video_end(){
  request_data = "video_end"
}