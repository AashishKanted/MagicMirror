setTimeout(updateTime, 1000);

function updateTime() {
    let d = new Date();
    var time = `${d.getHours()>9?d.getHours():"0"+d.getHours()} : ${d.getMinutes()>9?d.getMinutes():"0"+d.getMinutes()} : ${d.getSeconds()>9?d.getSeconds():"0"+d.getSeconds()}`
    document.getElementById("timeString").innerHTML= time
    setTimeout(updateTime,1000);
}