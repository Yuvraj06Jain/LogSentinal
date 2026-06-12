import DataButtons from "./components/DataButtons"
import DataTable from "./components/DataTable"
import FilterCard from "./components/FilterCard"
import Header from "./components/Header"

function Dashboard({
    socket,
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

export default Dashboard;