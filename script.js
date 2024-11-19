setTimeout(updateTime, 1000);
setTimeout(fetchSheetData, 1000);

const SHEET_ID = '12RAcvir3adNOZikeLpR35oprVppqx9aKzujgmbxBCHo';
const API_KEY = 'AIzaSyCg1F3hUA8cri7HHtvLiOwsfCxvbp4czfQ';
const RANGE = 'Sheet2'; // Adjust range as needed (e.g., "Sheet1!A1:D5")

async function fetchSheetData() {
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${SHEET_ID}/values/${RANGE}?key=${API_KEY}`;
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Error fetching data: ${response.statusText}`);
    }

    const data = await response.json();
    // console.log('Sheet Data:', data.values);

    var rem = document.getElementById("rem");
    var reminderString = "";

    for(var i=0; i<data.values.length-1 && i<5; i++){
        if(data.values[i+1][2]!=""){
            reminderString+= `<li class="bullet">${data.values[i+1][2]}</li> 
                    <li class="nobullet">@ ${data.values[i+1][3]}</li>`;
        }
    }
    rem.innerHTML=reminderString;

    var todo = document.getElementById("tod");
    var todoString = ""

    for(let i=0; i<data.values.length-1 && i<5; i++){
        if(data.values[i+1][2]!=""){
            // todo.insertRow(i).insertCell(0).innerHTML=`<li class="bullet">${data.values[i+1][2]}</li>`;
            todoString+=`<li class="bullet">${data.values[i+1][4]}</li>`;
        }
    }
    todo.innerHTML=todoString;

  } catch (error) {
    console.error('Error:', error);
  }

  setTimeout(fetchSheetData, 5000);
}


function updateTime() {
    let d = new Date();
    var time = `${d.getHours()>9?d.getHours():"0"+d.getHours()} : ${d.getMinutes()>9?d.getMinutes():"0"+d.getMinutes()} : ${d.getSeconds()>9?d.getSeconds():"0"+d.getSeconds()}`
    document.getElementById("timeString").innerHTML= time
    setTimeout(updateTime,1000);
}