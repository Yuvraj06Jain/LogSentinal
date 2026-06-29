import { useEffect, useState } from "react"
import React from "react";
import Markdown from 'react-markdown';
// FIX: useRef import dropped — `selected` is now useState, ref is unused.

function Summary({
    rooms,
    apacheLogs,
    nginxLogs,
    authLogs,
    setSummary,
    setMessage,
    socket
}){
    let min = new Date(); 
    min.setDate(min.getDate() - 30); 
    min = min.toISOString().slice(0,16);

    let x = new Date()
    x.setDate(x.getDate() - 7)

    let y = new Date()

    const [from, setFrom] = useState(x.toISOString())
    const [to, setTo] = useState(y.toISOString())
    const [logs, setLogs] = useState({})
    const [type, setType] = useState("")

    const [selected, setSelected] = useState({ Apache: [], Nginx: [], Auth: [] })

    useEffect(() => {
        if (rooms.length > 0) {
            setType(rooms[0])
        }
    }, [rooms])

    useEffect(() => {
        setLogs(
            (type==="Apache")? apacheLogs : 
            (type==="Nginx")? nginxLogs :
            (type==="Auth")? authLogs : {}
        )
    }, [type])

    
    function toggleField(currentType, field) {
        setSelected(prev => {
            const inc = prev[currentType].includes(field)
            return {
                ...prev,
                [currentType]: inc? 
                    prev[currentType].filter(f => f !== field) :
                    [...prev[currentType], field]
            }
        })
    }

    function toggleSelectAll(){
        const allFields = Object.keys(logs)
        const allSelected = allFields.length > 0 && allFields.every(f => selected[type]?.includes(f))

        setSelected(prev => ({
            ...prev,
            [type] : allSelected? [] : allFields
        }))
    }

    return (
        <div className = "fixed inset-0 z-50 bg-[#080c14]/80 flex flex-col items-center justify-center gap-2">
            <div className="w-150 h-90 bg-[#101720]/50 border border-[#1c2630] rounded-2xl flex flex-col justify-between items-center px-3 py-2">

                <div className="w-full h-10 flex px-3 justify-between items-center">

                    <div>
                        <label className="text-xs text-[#d7e4dd]/60 m-1 font-semibold">From: </label>
                        
                        <input type="datetime-local" className="border border-[#1c2630] rounded-xl active:border-[#1c2630] outline-none text-sm px-5 py-0.5 text-[#d7e4dd]/80" 
                        value={from.slice(0,16)}
                        min={min} max={to.slice(0,16) || new Date().toISOString().slice(0,16)} onChange={(e) => setFrom(new Date(e.target.value).toISOString())}></input>
                    </div>

                    <div>
                        <label className="text-xs text-[#d7e4dd]/60 m-1 font-semibold">To: </label>
                        <input type="datetime-local" className="border border-[#1c2630] rounded-xl active:border-[#1c2630] outline-none text-sm px-5 py-0.5 text-[#d7e4dd]/80" 
                        value={to.slice(0,16)}
                        min = {from.slice(0,16)} max = {new Date().toISOString().slice(0,16)} onChange={(e) => setTo(new Date(e.target.value).toISOString())}></input>
                    </div>

                </div>

                <div className="w-full flex justify-center items-center grow p-1 gap-2">

                    <div className="w-50 h-55  rounded-2xl flex flex-col justify-around items-center">

                        {
                            rooms.map((room) => (
                                <button key={room} onClick={() => setType(room)}className={`text-xs text-center font-semibold tracking-wider px-4 py-2 border-2 rounded-xl transition-colors ${(type === room)? "text-[#3cff9e] border-[#3cff9e] bg-[#3cff9e]/10" : "text-[#3cff9e]/60 border-[#3cff9e]/30"}`}>
                                {room}</button>
                            ))
                        }

                    </div>

                    <div className=" h-full w-0 border border-[#1c2630]/20"></div>

                    <div className="w-100 h-full rounded-2xl py-5 flex flex-col items-center">
                        <ul className="grid grid-cols-1 gap-3 w-80 max-h-65 overflow-y-scroll px-2 scrollbar-none">
                            
                            {
                                Object.keys(logs).map((field) => {
                                    const isOn = selected[type]?.includes(field)
                                    return (
                                        <li key={field}>
                                            <button type="button" onClick={() => toggleField(type, field)} className={`block w-full text-xs font-semibold border-2 rounded-lg py-1.5 text-center cursor-pointer transition-colors ${ isOn? "bg-[#3cff9e]/20 border-[#3cff9e] text-[#3cff9e]": "border-[#3cff9e]/30 text-[#3cff9e]/60 hover:bg-[#3cff9e]/20"}`}>
                                            {field}</button>
                                        </li>
                                    )
                                })
                            }

                        </ul>
                    </div>

                </div>

            </div>

            <div className="w-150 h-10 flex justify-between items-center px-1">

                <button className="text-xs text-center font-medium tracking-wider text-[#ff4d5e]  px-4 py-2 border border-[#ff4d5e]/40 rounded-lg hover:bg-[#ff4d5e]/20"
                onClick = {() => setSummary(false)}>
                    EXIT
                </button>
                
                <button className="text-xs text-center font-medium tracking-wider text-[#3cff9e]/70  px-4 py-2 border border-[#3cff9e]/30 rounded-lg hover:bg-[#3cff9e]/10"
                onClick = {() => {
                    toggleSelectAll()
                }}>
                    {Object.keys(logs).every(f => selected[type]?.includes(f)) ? "Deselect All" : "Select All"}
                </button>

                <button className="text-xs text-center font-medium tracking-wider text-[#3cff9e]  px-4 py-2 border border-[#3cff9e]/40 rounded-lg hover:bg-[#3cff9e]/20"
                onClick = {() => {
                    let flag = 0;
                    Object.values(selected).forEach((val) => {
                        if (val.length > 0){
                            flag = 1;
                        }
                    })
                    if (flag == 0){
                        setMessage({"Status" : "Info", "Message" : "Please select atleast one field..."})
                        setSummary(false)
                        return;
                    }

                    if(from === undefined || to === undefined){
                        setMessage({"Status" : "Info", "Message" : "Please select valid timeframe"})
                        setSummary(false)
                        return;
                    }

                    socket.emit("generateSummary", from, to, selected, (Response) => {
                        setMessage(Response);
                    })

                    setSummary(false)
                }}>
                
                SUBMIT</button>
            </div>
        </div>
    )
}

export default Summary