import { useEffect, useState, useRef } from "react"

import DataButtons from "./DataButtons"
import DataTable from "./DataTable"
import FilterCard from "./FilterCard"
import Header from "./Header"
import Summary from "./Summary"
import MessageBox from "./MessageBox"

function Dashboard({
    socket,
    setHome
}){

  let def = new Date();
  def.setDate(def.getDate() - 7);
  def = def.toISOString();

  const today = new Date().toISOString()

  const [summary, setSummary] = useState(false)

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
  
  const aggregateData = new Set(['URLs Accessed Counter', 'Suspicious IPs with No. of 404 errors >= 40%', 'No. of Failed login attempts per IP'])
  const detectFunc = {"Apache" : setApacheLogs, "Nginx" : setNginxLogs, "Auth" : setAuthLogs}

  useEffect(() => {
    socket.on("Real Time Logs Update", (allData) => {
        Object.entries(allData).forEach(([fileType, fileData]) => {
        console.log("Received New Logs Data for", fileType)
        if (Object.keys(fileData).length > 0){
          const func = detectFunc[fileType]
          func(prev => ({
            ...prev,
            ...Object.fromEntries(
              Object.entries(fileData).map(([key,val]) => [
                key,
                aggregateData.has(key)? val : [...(prev[key] || []), ...val]
              ])
            )
          }))
        }
        else{
          setMessage({"Status" : "Info", "Message" : `No new data received for ${fileType} logs`})
        }
      })
    })

    return () => socket.off("Real Time Logs Update")
  }, [])

  useEffect(() => {
    setRealLogs(currentRoom === "Apache"? apacheLogs : 
            currentRoom === "Nginx"? nginxLogs : 
            currentRoom === "Auth" ? authLogs : {})
  },[currentRoom, apacheLogs, nginxLogs, authLogs])
  
  
  useEffect(() => {
    socket.on("Updating Historical data of Apache logs", (data) => {
      console.log("Received Historical Apache Logs Data...");
      console.log(data)
      setApacheHisLogs(data)
    })

    return () => socket.off("Updating Historical data of Apache logs")
  }, [])
    
  useEffect(() => {
    socket.on("Updating Historical data of Nginx logs", (data) => {
      console.log("Received Historical Nginx Logs Data...");
      setNginxHisLogs(data)
    })

    return () => socket.off("Updating Historical data of Nginx logs")
  },[])

  useEffect(() => {
    socket.on("Updating Historical data of Auth logs", (data) => {
      console.log("Received Historical Auth Logs Data...");
      setAuthHisLogs(data)
    })

    return () => socket.off("Updating Historical data of Auth logs")
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
    if (currentRoom && show[currentRoom]["realTime"] !== undefined)
        return;
    setShow((prev) => {
      return {
        ...prev,
        [currentRoom]: {
          ...prev[currentRoom],
          "realTime": Object.keys(RealLogs)[0]
        }
      };
    });
  }, [RealLogs])


  return(
    <div className="fixed inset-0 -z-10 bg-[#080c14] font-['Space_Grotesk']" style={{backgroundImage: 'radial-gradient(circle, #d7e4dd22 1px, transparent 1px)', backgroundSize: '24px 24px'}} >
      {
        view[currentRoom] === "realTime" && (
        <div className="fixed left-0 right-0 top-0 h-40 pointer-events-none z-0" style={{ background: "linear-gradient(180deg, transparent, #3cff9e1a, transparent)", animation: "sweep 7s linear infinite" }}></div>
        )
      }

      <div className="flex flex-col h-screen">

        {/* Header */}
        <Header currentRoom={currentRoom} setCurrentRoom={setCurrentRoom} rooms={rooms} setHome={setHome} setView={setView} view={view[currentRoom]} pause={pause[currentRoom]} setPause={setPause} socket={socket} from={from} to={to} setSummary={setSummary}/>

        <div className="flex gap-4 px-6 pb-6 flex-1 min-h-0">

          {/* Left panel */}
          <div className="flex flex-col gap-3 w-100 shrink-0">

            {/* Data buttons card */}
            <DataButtons logs={view[currentRoom]==="realTime"? RealLogs : hisLogs} show={show} setShow={setShow} currentRoom={currentRoom} view={view[currentRoom]}/>

          </div>

          {/* Right panel */}
          <div className="gap-3 flex flex-col">

            {/* Filter Box */}
            <FilterCard from={from} to={to} setFrom={setFrom} setTo={setTo} view={view[currentRoom]} socket={socket} currentRoom={currentRoom} setMessage={setMessage}/>

            {/* Table */}
            <DataTable logs={view[currentRoom]==="realTime"? RealLogs : hisLogs} show={show} setShow={setShow} from={from} to={to} currentRoom={currentRoom} view={view[currentRoom]}/>

          </div>

        </div>

        <MessageBox message={message} />

      </div>
      
      {
        summary && <Summary rooms={rooms} apacheLogs={apacheLogs} nginxLogs={nginxLogs} authLogs={authLogs} setSummary={setSummary} socket={socket} setMessage={setMessage}></Summary>
      }
    </div>
  )
}

export default Dashboard;