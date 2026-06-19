function ActionButtons({
  pause,
  setPause,
  view,
  setView,
  from, 
  to,
  currentRoom,
  socket
}){
  return(
    <div className="flex gap-2 justify-center items-center">

      <input type="radio" name="view" id="History" className="hidden peer"></input>
      <label htmlFor="History" className={` cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-purple-800 hover:scale-110 duration-150
      ${ view==="historical"? "peer-checked:bg-purple-800" : "bg-transparent" }`} onClick = {() => {
        socket.emit("historical", currentRoom);
        setView((prev) => {
          return {
            ...prev,
            [currentRoom] : "historical"
          };
        });
      }}>Historical Data</label>

      <button className="cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-blue-500/60 hover:scale-110 duration-150" onClick = {() => {summaryGen(from, to)}}>
        Get Summary
      </button>

      <input type="radio" name="view" id="Real Time" className="hidden peer" defaultChecked></input>
      <label htmlFor="Real Time" className={`cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 hover:bg-green-600/90 hover:scale-110 duration-150 ${ view==="realTime"? "bg-green-600/90" : "bg-transparent" } `} onClick = {() => {
        setView((prev) => {
          return {
            ...prev,
            [currentRoom] : "realTime"
          };
        });
      }}>Real Time</label>

      <button className={` cursor-pointer text-sm font-bold border border-slate-700 rounded-lg p-2 text-slate-300 ${ !pause? "hover:bg-amber-400/80" : "hover:bg-green-500/80"} ${ view=="historical"? "opacity-50 pointer-events-none cursor-not-allowed" : "" } hover:scale-110 duration-150`} onClick={(prevValue) => {}}>{pause? "Resume" : "Pause"}</button>
    </div>
  )
}

export default ActionButtons