//import '../styles/home.css';
import React, { useState, useEffect } from 'react';
import Logo from '../logo.jpg'

const Home = ()=>{
    var form, container, failed; 
    var mid = 0;

    const handleSubmit = (e) =>{
        e.preventDefault();
        sendForm(form.elements["handle"].value, form.elements["status"].value, form.elements["unique"].value);
    }

    const sendForm = async(handle, status, unique)=>{
        console.log(handle, status,unique);
        if (status == "All") unique = "No";

        const res = await fetch(`https://bobxiong88.pythonanywhere.com/start?handle=${handle}&status=${status}&unique=${unique}`)
        const data = await res.json();

        mid = data.rid;
        console.log("hi", mid);
    }

    const handleUpdate = async () =>{
        const res = await fetch(`https://bobxiong88.pythonanywhere.com/get_status?rid=${mid}`);
        const data = await res.json();
        console.log(data.status, data.current, data.total);
        if (data.status == "starting"){
            console.log(1);
            failed.innerText = "Starting..."
        }
        else if (data.status == "failed"){
            console.log(2);
            failed.innerText = "Failed. Please enter a valid handle and try again."
            const okay = await fetch(`https://bobxiong88.pythonanywhere.com/done?rid=${mid}`);
            mid = 0;
        }
        else if (data.status == "downloading"){
            container.innerHTML = 
            `
            <div id = "download">Downloading...</div>
            <div id = "progress">
                <div id = "bar"></div>
            </div>
            <div id = "percent"></div>
            `
            console.log(3);
            var elem = document.getElementById("bar");
            var per = data.current/Math.max(1,data.total)*100;
            per = per.toFixed(1)+"%";
            elem.style.width = per;
            document.querySelector("#percent").innerText = per;
        }
        else{
            console.log(4);
            const url = `https://bobxiong88.pythonanywhere.com/download?rid=${mid}`
            container.innerHTML = 
            `
            <div id = "download">
                <a href = "${url}" >Click to download</a>
            </div>
            `
        }
    };
    useEffect(()=>{
        form = document.querySelector("#form");
        container = document.querySelector("#container");
        failed = document.querySelector("#failed");
    });

    useEffect(()=>{
        console.log("start");
    }, []);
    
    useEffect(() => {
        const interval = setInterval(async () => {
            console.log("Hiiiiii");
            if (mid != 0){
                await handleUpdate();
            }
        }, 500);
        return () => {
            clearInterval(interval);
        }
      }, []);

    return (
        <div className = "page" id = "home">
            <img src = {Logo} id = "logo"/>
            <div id = "container">
                <form action = "" id = "form" onSubmit = {handleSubmit}>
                    <div id = "handleContainer">
                        <label htmlFor = "handle">Handle:</label>
                        <input type = "text" id = "handle" name = "handle" required/>
                    </div>

                    <div id = "statusContainer">
                        <label htmlFor = "status">Status:</label>
                        <select name="status" id="status">
                            <option value="OK">AC</option>
                            <option value="WRONG_ANSWER">WA</option>
                            <option value="TIME_LIMIT_EXCEEDED">TLE</option>
                            <option value="RUNTIME_ERROR">RTE</option>
                            <option value="All">All</option>
                        </select>
                    </div>

                    <div id = "uniqueContainer">
                        <label htmlFor = "unique">Unique:</label>
                        <select name="unique" id="unique">
                            <option value="Yes">Yes</option>
                            <option value="No">No</option>
                        </select>
                    </div>

                    <button type = "submit" id = "submit">Submit</button>
                </form>
                <div id = "failed"></div>
            </div>
        </div>
    );
    
    
}

export default Home