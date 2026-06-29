import ActionButtons from "./ActionButtons";
import ViewButtons from "./ViewButtons";

function Header({
  setView,
  view,
  currentRoom,
  setCurrentRoom,
  setHome,
  rooms,
  from,
  to,
  socket,
  setSummary,
  setContact
}){
  return(
    <div className="w-screen bg-[#101720]/80 backdrop-blur-sm mb-20 py-2 flex justify-between items-center">
      
      <div className="flex gap-2 flex-1">
        <label htmlFor="logtype" className="text-sm text-[#d7e4dd]/60 font-semibold ml-4">LogType : </label>
        <select id="logtype" className="w-30 text-sm rounded-md px-2 py-0.5 outline-none bg-[#101720] border-[#1c2630] text-[#d7e4dd]" value={currentRoom}
        onChange={(e) => {setCurrentRoom(e.target.value)}}>
          {
            rooms.map((room) => (
              <option key={room} className="cursor-pointer">{room}</option>
            ))
          }
        </select>
      </div>

      <ViewButtons setView={setView} view={view} socket={socket} from={from} to={to} currentRoom={currentRoom}></ViewButtons>
        
      <ActionButtons setSummary={setSummary}socket={socket}view={view} currentRoom={currentRoom} setContact={setContact}></ActionButtons>

    </div>
  )
}

export default Header;