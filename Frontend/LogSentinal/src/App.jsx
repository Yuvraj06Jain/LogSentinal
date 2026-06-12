import { useEffect, useState } from "react"
import { io } from "socket.io-client"

// import DataButtons from "./components/DataButtons"
// import DataTable from "./components/DataTable"
// import FilterCard from "./components/FilterCard"
// import Header from "./components/Header"

let socket

function Home({
  setHome
}){
  return(
    <div className="fixed inset-0 -z-10 bg-slate-950" style={{backgroundImage: 'radial-gradient(circle, #ffffff22 1px, transparent 1px)', backgroundSize: '24px 24px'}}>
      <div className="min-h-screen flex flex-col items-center justify-center gap-5 text-center">
        <button className="font-extrabold text-9xl cursor-pointer text-cyan-500 active:text-slate-500 duration-100 " onClick = {() => {
          setHome(false)
          socket = io("http://localhost:8000")
          }}>
          LogSentinal</button>
        <p className="font-extrabold text-xl cursor-default text-slate-400 tracking-wide">Monitor your logs, Catch Threats before they catch you.</p>
      </div>
    </div>
  )
}

function Header({
  pause,
  setPause,
  setView,
  view,
  setCurrentRoom,
  setHome,
  rooms
}){
  return(
    <div className="w-screen h-10 bg-slate-950/80 backdrop-blur-sm shrink-0 mb-20 rounded-b-xl pt-3 flex justify-between items-center">

      <div className="flex gap-2">
        <label htmlFor="logtype" className="text-sm text-slate-400 ml-4">Active Log Monitoring : </label>
        <select id="logtype" className="text-sm  rounded-md px-2 py-0.5 outline-none bg-slate-800 border-slate-600 text-slate-200" onChange={(e) => {setCurrentRoom(e.target.value)}}>
          {
            rooms.map((room) => (
              <option key={room} className="cursor-pointer">{room}</option>
            ))
          }
        </select>
      </div>

      <ActionButtons setView={setView} view={view} pause={pause} setPause={setPause}/>

      <div>
        <button className="text-sm font-bold border border-slate-700 rounded-lg py-2 px-4 text-slate-300 hover:bg-red-500/60 hover:scale-110 duration-150 mr-4"
        onClick = {() => {
          socket.emit("EXIT")
          setHome(true)
          socket.close()
        }}>
          Exit
        </button>
      </div>

    </div>
  )
}

function DataButtons({
  logs,
  setShow
}){
  return(
    <div className="rounded-xl p-4 bg-slate-900 border border-slate-700">
      <p className="text-xs text-slate-400 mb-3">View</p>
      <ul className="grid grid-cols-1 gap-3">
        {
          Object.keys(logs).map((view) => (
            <li key={view}>
              <input type="radio" name="view" id={view} className="hidden peer" onClick = {() => {setShow(view)}} />
              <label htmlFor={view} className="block text-xs border border-slate-600 text-slate-300 rounded-lg py-1.5 text-center cursor-pointer hover:bg-cyan-500/10 peer-checked:bg-cyan-500/10 peer-checked:border-cyan-500/40 peer-checked:text-cyan-400">{view}</label>
            </li>
          ))
        }
      </ul>
    </div>
  )
}

function DataTable({
  logs,
  show,
  from,
  to
}){
  if(!show || !logs[show]?.length){
    return(
      <div className="w-full bg-slate-900 border border-slate-700 rounded-xl text-slate-700 text-center">
        No data available
      </div>
    )
  }

  return(
    <div className="w-full bg-slate-900 border border-slate-700 rounded-xl scrollbar-none overflow-scroll max-h-105">
      <table className="w-full text-sm table-fixed">

        <thead>
          <tr className="bg zinc-900 border border-slate-700 rounded-xl scrollbar-none overflow-scroll">
            {
              Object.keys(logs[show][0]).map((e) => (
                <th key = {e} className="text-left text-xs font-medium text-slate-400 px-3 py-2">{e}</th>
              ))
            }
          </tr>
        </thead>

        <tbody>
          {
            logs[show].map((dict, index) => (
              <tr key={index} className="border-b border-slate-700">
                {
                  Object.values(dict).map((value, i) => (
                    <td key={i} className="px-3 py-2 text-slate-100 text-xs">{value}</td>
                  ))
                }
              </tr>
            ))
          }
        </tbody>
      </table>
    </div>
  )
}



function ActionButtons({
  pause,
  setPause,
  view,
  setView,
  from, 
  to,
}){
  return(
    <div className="flex gap-2 justify-center items-center">
      <button className="cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-blue-500/60 hover:scale-110 duration-150" onClick = {() => {summaryGen(from, to)}}>
        Get Summary
      </button>

      <input type="radio" name="view" id="History" className="hidden peer"></input>
      <label htmlFor="History" className={` cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-purple-800
      ${ view==="history"? "peer-checked:bg-purple-800" : "bg-transparent" }`} onClick = {() => setView("history")}>History</label>

      <input type="radio" name="view" id="Real Time" className="hidden peer" defaultChecked></input>
      <label htmlFor="Real Time" className={`cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-green-600/50 ${ view==="real"? "bg-green-600/50" : "bg-transparent" } `} onClick = {() => setView("real")} >Real Time</label>

      <button className={` cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-amber-400/50 ${ pause ? "bg-amber-400/80" : "bg-transparent"}`} onClick={() => setPause((prev) => !prev)}>Pause</button>
    </div>
  )
}



function FilterCard({
  from,
  to,
}){
  return (
    <div className="rounded-xl bg-slate-900 border border-slate-700 flex justify-between items-center px-2 py-1.25 gap-4">
      <p className="text-sm text-slate-400 font-semibold">Filter Range</p>
      <div className="flex justify-evenly flex-1 ">
        <div className="">
          <label className="text-xs text-zinc-400 m-1 font-semibold">From: </label>
          <input className="border border-slate-700 rounded-xl active:border-slate-600 outline-none text-sm px-5 py-0.5 text-slate-300 w-80" placeholder="DD/MM/YY" value={from}></input>
        </div>
        <div className="">
          <label className="text-xs text-zinc-400 m-1 font-semibold">To: </label>
          <input className="border border-slate-700 rounded-xl active:border-slate-600 outline-none text-sm px-5 py-0.5 text-slate-300 w-80" placeholder="DD/MM/YY" value={to}></input>
        </div>
      </div>
      <div className=" h-full w-0 border border-slate-600"></div>
      <div className="flex justify-center items-center mr-2">
        <button className="text-sm font-bold  rounded-lg py-2 px-2 text-slate-300 hover:bg-orange-500 hover:scale-105 duration-150 cursor-pointer" onClick = {() => {
          socket.emit("Refresh")
        }}>
          Refresh
        </button>
      </div>
    </div>
  )
}


function Dashboard({
  setHome
}){
  const [from, setFrom] = useState("latest")
  const [to, setTo] = useState("latest")
  const [apacheLogs, setApacheLogs] = useState({})
  const [nginxLogs, setNginxLogs] = useState({})
  const [authLogs, setAuthLogs] = useState({})
  const [show, setShow] = useState()
  const [rooms, setRooms] = useState([])
  const [currentRoom, setCurrentRoom] = useState()
  const [ref, setRef] = useState(false)
  const [view, setView] = useState("real")
  const [pause, setPause] = useState(false)

  useEffect(() => {
    socket.on("Apache Logs Update", (data) => {
      console.log("Received Apache Log Data...");
      setApacheLogs(data);
    })
    return () => socket.off("Apache Logs Update")
  },[])

  useEffect(() => {
    socket.on("Nginx Logs Update", (data) => {
      console.log("Received Nginx Log Data...");
      setNginxLogs(data)
    })
    return () => socket.off("Nginx Logs Update")
  },[])

  useEffect(() => {
    socket.on("Auth Logs Update", (data) => {
      console.log("Received Auth Log Data...");
      setAuthLogs(data);
    })
    return () => socket.off("Auth Logs Update")
  },[])
  
  useEffect(() => {
    socket.on("Active Rooms", (data) => {
      console.log("Recieved Rooms Data ... ")
      setRooms(data)
    })
  }, [])

  useEffect(() => {
    if (rooms.length && !currentRoom) setCurrentRoom(rooms[0])
  },[rooms])

  const logs = currentRoom === "Apache"? apacheLogs : currentRoom === "Nginx"? nginxLogs : currentRoom === "Auth" ? authLogs : {}

  return(
    <div className="fixed inset-0 -z-10 bg-slate-950" style={{backgroundImage: 'radial-gradient(circle, #ffffff22 1px, transparent 1px)', backgroundSize: '24px 24px'}}>
      <div className="flex flex-col h-screen">
        {/* Header */}
        <Header apacheLogs={apacheLogs} nginxLogs={nginxLogs} authLogs={authLogs} setCurrentRoom={setCurrentRoom} rooms={rooms} setHome={setHome} setView={setView} view={view} pause={pause} setPause={setPause}/>

        <div className="flex gap-4 px-6 pb-6 flex-1 min-h-0">
          {/* Left panel */}
          <div className="flex flex-col gap-3 w-100 shrink-0">

            {/* Data buttons card */}
            <DataButtons logs={logs} show={show} setShow={setShow}/>

          </div>

          {/* Right panel */}
          <div className="gap-3 flex flex-col">
            {/* Filter Box */}
            <FilterCard from={from} to={to} />
            {/* Table */}
            <DataTable logs={logs} show={show} from={from} to={to}/>

          </div>

        </div>

    </div>

  </div>
  )
}

function App(){
  const [home, setHome] = useState(true)

  return (
    <>
      {
        home && <Home setHome={setHome}/>
      }
      {
        !home && <Dashboard setHome = {setHome}/>
      }
    </>
  )
}

export default App

