import { useEffect, useState, useRef } from "react"

import DataButtons from "./DataButtons"
import DataTable from "./DataTable"
import FilterCard from "./FilterCard"
import Header from "./Header"

function Dashboard({
    socket,
    setHome
}){

  let def = new Date();
  def.setDate(def.getDate() - 30);
  def = def.toISOString();

  const today = new Date().toISOString()

  const [from, setFrom] = useState(def)
  const [to, setTo] = useState(today)

  const [RealLogs, setRealLogs] = useState({})
  const [apacheLogs, setApacheLogs] = useState({})
  const [nginxLogs, setNginxLogs] = useState({})
  const [authLogs, setAuthLogs] = useState({})

  
  const [hisLogs, setHisLogs] = useState({})
  const [apacheHisLogs, setApacheHisLogs] = useState({})
  const [nginxHisLogs, setNginxHisLogs] = useState({})
  const [authHisLogs, setAuthHisLogs] = useState({})


  const [rooms, setRooms] = useState([])
  const [currentRoom, setCurrentRoom] = useState()

  const [show, setShow] = useState({"Apache" : {"realTime" : undefined, "historical" : undefined},
                                    "Nginx" : {"realTime" : undefined, "historical" : undefined}, 
                                    "Auth" : {"realTime" : undefined, "historical" : undefined}})

  const [view, setView] = useState({"Apache" : "realTime",
                                    "Nginx" : "realTime",
                                    "Auth" : "realTime",
                                    undefined : "realTime"})

  const [pause, setPause] = useState({"Apache" : false,
                                      "Nginx" : false,
                                      "Auth" : false})

  const [message, setMessage] = useState("")
  
  const aggregateData = new Set(['URLs Accessed Counter', 'Suspicious IPs with No. of 404 errors > 40%', 'No. of Failed login attempts per IP'])

  useEffect(() => {
    socket.on("Apache Logs Update", (data) => {
      console.log("Received Apache Logs Data...", data);
      setApacheLogs((prev) => ({
        ...prev,
        ...Object.fromEntries(
          Object.entries(data).map(([key, val]) => [
            key,
            aggregateData.has(key) ? val : [...(prev[key] || []), ...val]
          ])
        )
      }))
    })
    
    socket.on("Nginx Logs Update", (data) => {
      console.log("Received Nginx Logs Data...");
      setNginxLogs((prev) => ({
        ...prev,
        ...Object.fromEntries(
          Object.entries(data).map(([key,val]) => [
            key,
            aggregateData.has(key)? val : [...(prev[key] || []), ...val]
          ])
        )
      }))
    })

    socket.on("Auth Logs Update", (data) => {
      console.log("Received Auth Logs Data...");
      setAuthLogs((prev) => ({
        ...prev,
        ...Object.fromEntries(
          Object.entries(data).map(([key,val]) => [
            key,
            aggregateData.has(key)? val : [...(prev[key] || []), ...val]
          ])
        )
      }))
    })
  },[])

  useEffect(() => {
    setRealLogs(currentRoom === "Apache"? apacheLogs : 
            currentRoom === "Nginx"? nginxLogs : 
            currentRoom === "Auth" ? authLogs : {})
  },[currentRoom, apacheLogs, nginxLogs, authLogs])
  
  

  useEffect(() => {
    socket.on("Updating Historical data of Apache logs", (data) => {
      console.log("Received Historical Apache Logs Data...");
      if(data.Status === "Success")
        setApacheHisLogs(data.Message)
      else
        setMessage(data.Message)
    })
    
    socket.on("Updating Historical data of Nginx logs", (data) => {
      console.log("Received Historical Nginx Logs Data...");
      if(data.Status === "Success")
        setNginxHisLogs(data.Message)
      else
        setMessage(data.Message)
    })

    socket.on("Updating Historical data of Auth logs", (data) => {
      console.log("Received Historical Auth Logs Data...");
      if(data.Status === "Success")
        setAuthHisLogs(data.Message)
      else
        setMessage(data.Message)
    })
  },[])

  useEffect(() => {
    setHisLogs(currentRoom === "Apache"? apacheHisLogs : 
            currentRoom === "Nginx"? nginxHisLogs : 
            currentRoom === "Auth" ? authHisLogs : {})
  },[currentRoom, apacheHisLogs, nginxHisLogs, authHisLogs])


  
  useEffect(() => {
    socket.on("Sending Rooms Data...", (data) => {
      console.log("Recieved Rooms Data ... ")
      setRooms(data)
    })

    return () => socket.off("Sending Rooms Data...")
  }, [])



  useEffect(() => {
    if (rooms.length && !currentRoom) setCurrentRoom(rooms[0])
  },[rooms])


  useEffect(() => {
    if(currentRoom && !show[currentRoom][view]) console.log(currentRoom, show[currentRoom][view])

    setShow((prev) => {
      return {
        ...prev, [currentRoom] : {
          ...prev[currentRoom],
          "realTime" : Object.keys(RealLogs)[0]
        }
      };
    });
    console.log(show)
  },[RealLogs])


  useEffect(() => {
    socket.emit("pause_resume", (Response) => {
      setMessage(Response.Message)
    });
  },[pause[currentRoom]])

  return(
    <div className="fixed inset-0 -z-10 bg-black" style={{backgroundImage: 'radial-gradient(circle, #ffffff22 1px, transparent 1px)', backgroundSize: '24px 24px'}}>

      <div className="flex flex-col h-screen">

        {/* Header */}
        <Header currentRoom={currentRoom} setCurrentRoom={setCurrentRoom} rooms={rooms} setHome={setHome} setView={setView} view={view[currentRoom]} pause={pause[currentRoom]} setPause={setPause} socket={socket} from={from} to={to}/>

        <div className="flex gap-4 px-6 pb-6 flex-1 min-h-0">

          {/* Left panel */}
          <div className="flex flex-col gap-3 w-100 shrink-0">

            {/* Data buttons card */}
            <DataButtons logs={view[currentRoom]==="realTime"? RealLogs : hisLogs} show={show} setShow={setShow} currentRoom={currentRoom} view={view[currentRoom]}/>

          </div>

          {/* Right panel */}
          <div className="gap-3 flex flex-col">

            {/* Filter Box */}
            <FilterCard from={from} to={to} setFrom={setFrom} setTo={setTo} view={view[currentRoom]} socket={socket}/>

            {/* Table */}
            <DataTable logs={view[currentRoom]==="realTime"? RealLogs : hisLogs} show={show} from={from} to={to} currentRoom={currentRoom} view={view[currentRoom]}/>

          </div>

        </div>

      </div>

      {/* Message */}
      <div className="w-40 h-20 bottom-1 right-1 border">
        
      </div>

    </div>
  )
}

export default Dashboard;