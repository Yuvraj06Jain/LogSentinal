import ActionButtons from "./ActionButtons";

function Header({
  pause,
  setPause,
  setView,
  view,
  currentRoom,
  setCurrentRoom,
  setHome,
  rooms,
  from,
  to,
  socket
}){
  return(
    <div className="w-screen h-10 bg-transparent backdrop-blur-sm shrink-0 mb-20 rounded-b-xl pt-3 flex justify-between items-center">

      <div className="flex gap-2">
        <label htmlFor="logtype" className="text-sm text-slate-400 ml-4">Monitoring For : </label>
        <select id="logtype" className="text-sm  rounded-md px-2 py-0.5 outline-none bg-slate-800 border-slate-600 text-slate-200" onChange={(e) => {setCurrentRoom(e.target.value)}}>
          {
            rooms.map((room) => (
              <option key={room} className="cursor-pointer">{room}</option>
            ))
          }
        </select>
      </div>

      <ActionButtons setView={setView} view={view} pause={pause} setPause={setPause} socket={socket} from={from} to={to} currentRoom={currentRoom}/>

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

export default Header;