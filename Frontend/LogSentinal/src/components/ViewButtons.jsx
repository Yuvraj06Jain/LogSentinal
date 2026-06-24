function ViewButtons({
  view,
  setView,
  from, 
  to,
  currentRoom,
  socket
}){
  return(
    <div className="flex gap-5 justify-center items-center  flex-none shrink-0">

      <input type="radio" name="view" id="History" className="hidden peer" checked={view === "historical"}></input>
      <label htmlFor="History" className={` cursor-pointer text-sm font-bold border border-[#1c2630] rounded-lg p-2 text-[#d7e4dd]/70 hover:bg-[#d7e4dd]/10 hover:scale-110 duration-150
      ${ view==="historical"? "peer-checked:bg-[#d7e4dd]/10" : "bg-transparent" }`}
      onClick = {() => {
        setView((prev) => {
          return {
            ...prev,
            [currentRoom] : "historical"
          };
        });
      }}>Historical Data</label>

      <input type="radio" name="view" id="Real Time" className="hidden peer" defaultChecked checked={view === "realTime"}></input>
      <label htmlFor="Real Time" className={`cursor-pointer text-sm font-bold border border-[#3cff9e] rounded-lg p-2 text-[#3cff9e] hover:bg-[#3cff9e]/20 hover:scale-110 duration-150 ${ view==="realTime"? "bg-[#3cff9e]/15" : "bg-transparent" } `} onClick = {() => {
        setView((prev) => {
          return {
            ...prev,
            [currentRoom] : "realTime"
          };
        });
      }}>
        Real Time {view==="realTime" && (<span className="inline-block w-2 h-2 rounded-full bg-[#3cff9e] ml-2 animate-pulse" style={{animationDuration: `${1}s`}} ></span>)}
      </label>

    </div>
  )
}

export default ViewButtons