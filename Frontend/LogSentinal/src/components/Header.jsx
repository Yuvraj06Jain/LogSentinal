import ActionButtons from "./ActionButtons";
import ViewButtons from "./ViewButtons";

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
  socket,
  setSummary
}){
  return(
    <div className="w-screen h-10 bg-slate-950/80 backdrop-blur-sm shrink-0 mb-20 rounded-b-xl pt-3 flex justify-between items-center">
      
      <div className="flex gap-2 flex-1">
        <label htmlFor="logtype" className="text-sm text-slate-400 font-semibold ml-4">Monitoring For : </label>
        <select id="logtype" className="w-30 text-sm rounded-md px-2 py-0.5 outline-none bg-slate-800 border-slate-600 text-slate-200 " onChange={(e) => {setCurrentRoom(e.target.value)}}>
          {
            rooms.map((room) => (
              <option key={room} className="cursor-pointer">{room}</option>
            ))
          }
        </select>
      </div>

      <ViewButtons setView={setView} view={view} socket={socket} from={from} to={to} currentRoom={currentRoom}></ViewButtons>
        
      <ActionButtons setSummary={setSummary} pause={pause} setPause={setPause} socket={socket} setHome={setHome} view={view} currentRoom={currentRoom}></ActionButtons>

    </div>
  )
}

export default Header;