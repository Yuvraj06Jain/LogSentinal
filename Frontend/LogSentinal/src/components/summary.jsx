import { useEffect, useState } from "react"
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

    let from = new Date()
    from.setDate(from.getDate() - 7)
    from = from.toISOString().slice(0,16)

    let to = new Date()
    to = to.toISOString().slice(0,16)

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
        <div className = "fixed inset-0 z-50 bg-gray-950/80 flex flex-col justify-center items-center gap-2">
            <div className="w-150 h-90 bg-slate-900/50 border border-slate-700 rounded-2xl flex flex-col justify-between items-center px-3 py-2">

                <div className="w-full h-10 flex px-3 justify-between items-center">

                    <div>
                        <label className="text-xs text-zinc-400 m-1 font-semibold">From: </label>
                        
                        <input type="datetime-local" className="border border-slate-700 rounded-xl active:border-slate-600 outline-none text-sm px-5 py-0.5 text-slate-300"
                        min={min} max={to || new Date().toISOString().slice(0,16)}></input>
                    </div>

                    <div>
                        <label className="text-xs text-zinc-400 m-1 font-semibold">To: </label>
                        <input type="datetime-local" className="border border-slate-700 rounded-xl active:border-slate-600 outline-none text-sm px-5 py-0.5 text-slate-300"
                        min = {from} max = {new Date().toISOString().slice(0,16)}></input>
                    </div>

                </div>

                <div className="w-full flex justify-center items-center grow p-1 gap-2">

                    <div className="w-50 h-55  rounded-2xl flex flex-col justify-around items-center">

                        {
                            rooms.map((room) => (
                                <button key={room} onClick={() => setType(room)}className={`text-xs text-center font-semibold tracking-wider px-4 py-2 border-2 rounded-xl transition-colors ${(type === room)? "text-cyan-300 border-cyan-500 bg-cyan-500/10" : "text-cyan-400 border-cyan-900"}`}>
                                {room}</button>
                            ))
                        }

                    </div>

                    <div className=" h-full w-0 border border-slate-600/20"></div>

                    <div className="w-100 h-full rounded-2xl py-5 flex flex-col items-center">
                        <ul className="grid grid-cols-1 gap-3 w-80 max-h-65 overflow-y-scroll px-2 scrollbar-none">
                            
                            {
                                Object.keys(logs).map((field) => {
                                    const isOn = selected[type]?.includes(field)
                                    return (
                                        <li key={field}>
                                            <button type="button" onClick={() => toggleField(type, field)} className={`block w-full text-xs font-semibold border-2 rounded-lg py-1.5 text-center cursor-pointer transition-colors ${ isOn? "bg-cyan-500/20 border-cyan-500 text-cyan-300": "border-cyan-900 text-cyan-400 hover:bg-cyan-500/20"}`}>
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

                <button className="text-xs text-center font-medium tracking-wider text-red-600  px-4 py-2 border border-red-700/40 rounded-lg hover:bg-red-700/20"
                onClick = {() => setSummary(false)}>
                    EXIT
                </button>
                
                <button className="text-xs text-center font-medium tracking-wider text-cyan-400  px-4 py-2 border border-cyan-900/40 rounded-lg hover:bg-cyan-700/10"
                onClick = {() => {
                    toggleSelectAll()
                }}>
                    {Object.keys(logs).every(f => selected[type]?.includes(f)) ? "Deselect All" : "Select All"}
                </button>

                <button className="text-xs text-center font-medium tracking-wider text-green-500  px-4 py-2 border border-green-600/40 rounded-lg hover:bg-green-400/20"
                onClick={() => { socket.emit("GenerateSummary", from, to, selected, (Response) => {setMessage(Response)}); setSummary(false); }}>
                
                SUBMIT</button>
            </div>
      </div>
    )
}

export default Summary