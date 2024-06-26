class Image {
    constructor(data){
        this.buffers = data.buffers
        this.width = data.width
        this.height = data.height
        this.alt = data.alt
    }
}
class Video {
    constructor(data){
        this.buffers = data.buffers
        this.width = data.width
        this.height = data.height
        this.autoplay = data.autoplay
        this.controls = data.controls
        // this.type = data.type
    }
}

function load_gif(name,index,src){
    var image = document.createElement("img")
    image.src = src
    image.width = default_gif.width
    image.height = default_gif.height
    image.alt = default_gif.alt
    if(typeof default_gif.buffers[name]!="object"){
        default_gif.buffers[name]=[]
    }
    default_gif.buffers[name][index] = image
}

function load_image(name,src){
    var image = document.createElement("img")
    image.src = src
    image.width = default_images.width
    image.height = default_images.height
    image.alt = default_images.alt
    default_images.buffers[name] = image
}

function load_video(name,src){
    var video = document.createElement('video')
    video.src = src
    video.width = default_videos.width
    video.height = default_videos.height
    video.autoplay = default_videos.autoplay
    video.controls = default_videos.controls
    video.muted = default_videos.muted
    default_videos.buffers[name] = video
}

function remove_gif(name){
    if(default_gif.buffers.hasOwnProperty(name)){
        delete default_gif.buffers['name']
    }
}

function remove_image(name){
    if(default_images.buffers.hasOwnProperty(name)){
        delete default_images.buffers['name']
    }
}

function remove_video(){
    if(default_videos.buffers.hasOwnProperty(name)){
        delete default_videos.buffers['name']
    }
}


function display_gif(name,index){
    // remove_video()
    var image_box = document.getElementById("display_image")
    image_box.src = default_gif.buffers[name][index].src
    image_box.alt = default_gif.alt
    image_box.width = default_gif.width
    image_box.height = default_gif.height
    image_visibility()
}

// function display_image(src){
//     // remove_video()
//     var aaa = document.getElementById("display_image")

//     aaa.src = src
//     // image_visibility()
// }

// function display_video(src){
//     // remove_image()
//     var aaa = document.getElementById("display_video")

//     aaa.src = src
//     video_visibility()
// }

function display_image(name){
    // remove_video()
    var image_box = document.getElementById("display_image")
    image_box.src = default_images.buffers[name].src
    image_box.alt = default_images.alt
    image_box.width = default_images.width
    image_box.height = default_images.height
    image_visibility()
}

function display_video(name){
    // remove_image()
    var video_box = document.getElementById("display_video")
    video_box.src = default_videos.buffers[name].src
    video_box.width = default_videos.width
    video_box.height = default_videos.height
    default_videos.buffers[name].addEventListener('ended',
        function haha() { 
            onVideoEnded(Date.now());
            default_videos.buffers[name].removeEventListener('ended',haha,false)
    },false)
    video_visibility()
    video_box.play()
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

// function remove_image(){
//     image_box.src = ""
//     image_box.width = 0
//     image_box.height = 0
//     image_box.alt = ""
// }

// function remove_video(){
//     video_box.src = ""
//     video_box.width = 0
//     video_box.height = 0
// }

function update_text(value){
    const information = document.getElementById('info')
    information.innerText = value
}

function onVideoEnded(name) {
    update_text(name)
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
var default_images = new Image({buffers:{},width:1920,height:1080,alt:"image"})
var default_videos = new Video({buffers:{},width:1920,height:1080,autoplay:true,controls:false,muted:false})
var default_gif = new Image({buffers:{},width:1920,height:1080,alt:"gif"})
var image_box = document.getElementById("display_image")
var video_box = document.getElementById("display_video")
// var demo_box = document.getElementById("demo_box")
// var container = document.getElementById("text")
// container.innerText = demo_box.hasChildNodes()

module.exports = {
    load_gif,
    load_image,
    load_video,
    remove_gif,
    remove_image,
    remove_video,
    display_gif,
    display_image,
    display_video,
    display_camera,
    update_text,
    server_command
}