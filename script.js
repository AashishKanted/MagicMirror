setTimeout(updateTime, 1000);
setTimeout(appendData, 1000);

function updateTime() {
    let d = new Date();
    var time = `${d.getHours()>9?d.getHours():"0"+d.getHours()} : ${d.getMinutes()>9?d.getMinutes():"0"+d.getMinutes()} : ${d.getSeconds()>9?d.getSeconds():"0"+d.getSeconds()}`
    document.getElementById("timeString").innerHTML= time
    setTimeout(updateTime,1000);
}


function appendData(){
    fetch("./data.json")
    .then((res) => {
        if (!res.ok) {
            throw new Error
                (`HTTP error! Status: ${res.status}`);
        }
        return res.json();
    })
    .then((data) => {
        var rem = document.getElementById("rem");
        for(let i=0; i<data.reminders.length && i<5; i++){
            rem.insertRow(i).insertCell(0).innerHTML=`<li class="bullet">${data.reminders[i][0]}</li> 
                                                    <li class="nobullet">@ ${data.reminders[i][1]}</li>`;
        }
        var todo = document.getElementById("tod");
        for(let i=0; i<data.todo.length && i<10; i++){
            todo.insertRow(i).insertCell(0).innerHTML=`<li class="bullet">${data.todo[i]}</li>`;
        }
    })
    .catch((error) =>
        console.error("Unable to fetch data:", error));

        
}