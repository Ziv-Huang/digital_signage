module.exports = {
    load_image,
    load_video,
    remove_image,
    remove_video,
    display_image,
    display_video,
    display_camera,
    update_text,
    server_command
}

const preload = require('./preload')

function load_image(name,src){
    default_images.buffers[name] = src
}

function load_video(name,src){
    default_videos.buffers[name] = src
}

function remove_image(name){
    if(default_images.buffers.hasOwnProperty(name)){
        delete default_images.buffers['name']
    }
}

function remove_video(name){
    if(default_videos.buffers.hasOwnProperty(name)){
        delete default_videos.buffers['name']
    }
}

function display_image(name){
    var image_box = document.getElementById("display_image")
    image_box.src = default_images.buffers[name]
    image_visibility()
}

function display_video(name){
    var video_box = document.getElementById("display_video")
    video_box.src = default_videos.buffers[name]
    video_box.addEventListener('ended',
        function() { 
            onVideoEnded();
    })
    video_box.load()
    video_box.play()
    video_visibility()
}

function display_camera(value){
    var image_box = document.getElementById("display_image")
    image_box.src = "data:image/jpeg;base64," + value
    image_visibility()
}

function image_visibility(){
    var image_box = document.getElementById("display_image")
    var video_box = document.getElementById("display_video")
    image_box.style.visibility = "visible"
    video_box.style.visibility = "hidden"
}

function video_visibility(){
    var image_box = document.getElementById("display_image")
    var video_box = document.getElementById("display_video")
    video_box.style.visibility = "visible"
    image_box.style.visibility = "hidden"
}

function update_text(value){
    const information = document.getElementById('info')
    information.innerText = value
}

function onVideoEnded() {
    preload.send_video_end()
}

function server_command(packet){

    // data format
    // {
    //     "command":"load_image",
    //     "data":{
    //         "name":XXX,
    //         "src":XXX
    //     }
    // }

    const action = packet.command
    const data = packet.data
    switch (action) {
    case 'load_gif': {
            load_gif(data.name,data.index,data.src)
            break
        }
        case 'load_image': {
            load_image(data.name,data.src)
            break
        }
        case 'load_video': {
            load_video(data.name,data.src)
            break
        }
        case 'display_gif': {
            display_gif(data.name,data.index)
            break
        }
        case 'display_image': {
            display_image(data.name)
            break
        }
        case 'display_video': {
            display_video(data.name)
            break
        }
        case 'display_camera': {
            display_camera(data.value)
            break
        }
        case 'update_text': {
            update_text(data.value)
            break
        }
        default: {
            break;
        }
    }
}

// ### init ###
var default_images = {buffers:{}}
var default_videos = {buffers:{}}
// var demo_box = document.getElementById("demo_box")
// var container = document.getElementById("text")
// container.innerText = demo_box.hasChildNodes()