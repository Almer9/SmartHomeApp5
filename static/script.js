function toggleLight(room) {
    let lightElement = document.getElementById(room + "lightimg")
    console.log(room)
    $.ajax({
        url: `/${room}/light/toggle`,
        type: 'GET',
        success: function (response) {
            console.log(response)
            if (response.state) {
                lightElement.src = "static/light-bulb-on.png"
            } else {
                lightElement.src = "static/light-bulb.png"
            }
        },
        error: function (jqXHR, exception) {
            console.log(jqXHR, exception)
        }
    })

}

function changeBrightness(room) {
    let lightBrightness = document.getElementById(room + "Brightness")
    let brightnessField = document.getElementById(room + "brightnessfield")
    let serverData = {
        'brightness': brightnessField.value
    }
    if (brightnessField.value > 0 && brightnessField.value <= 100) {
        $.ajax({
            url: `/${room}/light/brightness`,
            type: 'POST',
            data: serverData,
            success: function (response) {
                lightBrightness.innerText = `Brightness: ${response.brightness}`
                brightnessField.value = ""
            }
        })
    }


}

async function getHeating(onSuccess) {

    const response = await fetch('/kitchen/temp/getinfo');
    if (response.ok) {
        onSuccess(await response.json())
    }

}

async function getOnoff(onSuccess) {

    const response = await fetch('/kitchen/temp/getonoff');
    if (response.ok) {
        onSuccess(await response.json())
    }

}


async function toggleTemp() {
    getTempThresholds();

    let tempelem = document.getElementById("kitchentempvalue")
    let heating = true
    let heatingStatusLabel = document.getElementById("heatingStatusLabel")
    let systemStatusLabel = document.getElementById("systemStatusLabel")
    let systemStatus

    await getHeating(function (response) {
        if (response.systemstatus) {
            systemStatusLabel.innerText = "System is on"
        } else {
            systemStatusLabel.innerText = "System is off"
        }
        systemStatus = response.systemstatus

        if (!response.heating && response.temp >= response.on_temp && response.temp <= response.off_temp || response.temp >= response.off_temp) {
            heating = false
            heatingStatusLabel.innerText = "Heating system is off"
        } else {
            heatingStatusLabel.innerText = "Heating system is on"
        }
    })
    console.log(systemStatus)
    if (systemStatus === 1) {

        let data = {'temp': tempelem.innerText, 'heating': heating}
        $.ajax({
            url: '/none/temp/update',
            type: 'POST',
            data: data,
            success: function (response) {
                tempelem.innerText = response.temp
                const now = new Date();
                const hours = now.getHours();
                const minutes = now.getMinutes();
                const seconds = now.getSeconds();
                const formattedTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
                addData(formattedTime, response.temp)
            }
        });

        $.ajax({
            url: '/none/temp/update',
            type: 'GET',
            success: function (response) {

            }
        });
    }
}

function getTempThresholds() {
    $.ajax({
        url: '/kitchen/temp/getinfo',
        type: 'GET',
        success: function (response) {
            console.log(response)
            let offvalue = document.getElementById("offlabel")
            let onvalue = document.getElementById("onlabel")
            offvalue.innerHTML = `MAX: ${response.off_temp}`
            onvalue.innerHTML = `MIN: ${response.on_temp}`
        }
    });

}

function changeTempThresholds() {
    let on_temp = document.getElementById("onvaluefield")
    let off_temp = document.getElementById("offvaluefield")
    if (on_temp) {
        $.ajax({
            url: '/kitchen/temp/changethresholds',
            type: 'POST',
            data:
                {
                    temp: on_temp.value,
                    temp_kind: 'low',
                },
            success: function (response) {
                let value = document.getElementById("onlabel")
                value.innerHTML = `MIN: ${response.temp}`
                on_temp.value = ""
            }
        });
    }

    if (off_temp) {
        $.ajax({
            url: '/kitchen/temp/changethresholds',
            type: 'POST',
            data:
                {
                    temp: off_temp.value,
                    temp_kind: 'high',
                },
            success: function (response) {
                let value = document.getElementById("offlabel")
                value.innerHTML = `MAX: ${response.temp}`
                off_temp.value = ""

            }
        });
    }
}

function onOff(){
    let systemStatusLabel = document.getElementById("systemStatusLabel")
    $.ajax({
            url: '/kitchen/temp/onoff',
            type: 'POST',
            success: function (response) {
                if (response.systemstatus){
                    systemStatusLabel.innerText = "System is on"
                }
                else {
                    systemStatusLabel.innerText = "System is off"
                }

            }
        });

}


function addData(time, temp) {
    console.log(myChart)
    console.log(time)
    console.log(temp)
    myChart.data.labels.push(time);
    myChart.data.datasets[0].data.push({x: time, y: temp});
    myChart.update();
}
